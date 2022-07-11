import jwt, requests, boto3

from django.views           import View
from django.conf            import settings
from django.db              import transaction
from django.http            import JsonResponse

from users.models           import SocialAccount, User
from authors.models         import Author

from utils.fileuploader_api import FileUploader, FileHandler, image_extension_list
from utils.login_decorator  import login_decorator


config = {
    "bucket" : settings.AWS_STORAGE_BUCKET_NAME
}
file_uploader = FileUploader(boto3.client('s3'), config)
file_handler = FileHandler(file_uploader)

class KakaoLoginView(View):
    def get(self, request):
        try:
            code = request.GET.get("code")
            kakao_token_api = "https://kauth.kakao.com/oauth/token"
            data = {
                "grant_type"  : "authorization_code",
                "client_id"   : settings.CLIENT_ID,
                "redirect_uri": "http://localhost:3000/oauth/callback/kakao",
                "code"        : code
            }
            access_token  = requests.post(kakao_token_api, data=data, timeout=1).json()["access_token"]
            kakao_api_url = "https://kapi.kakao.com/v2/user/me"

            response = requests.get(kakao_api_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=1)
            if response.status_code == 401:
                return JsonResponse({"Error":"token_error"}, status = 401)

            user_info = response.json()
            sociaaccount = SocialAccount.objects.filter(social_account_id  = user_info["id"])
            if sociaaccount.exists():
                access_token = jwt.encode({'id': sociaaccount.get().id}, settings.SECRET_KEY, settings.ALGORITHM)
                return JsonResponse({"token":access_token}, status = 200)
            
            
            with transaction.atomic():
                user=User.objects.create(
                        email        = user_info["kakao_account"]["email"],
                        name         = user_info["properties"]["nickname"],
                        thumbnail    = user_info["properties"]["profile_image"],
                        introduction = user_info["properties"]["nickname"]+"님의 BranchTime입니다"
                    )
                SocialAccount.objects.create(
                        social_account_id = user_info["id"],
                        name              = "kakao",
                        user_id           = user.id
                        )
                access_token = jwt.encode({'id':user.id}, settings.SECRET_KEY, settings.ALGORITHM)  
                return JsonResponse({"token":access_token}, status = 200)
        except KeyError:
            return JsonResponse({"message":"KEY ERROR"}, status = 400)    

class UserDetailView(View):
    @login_decorator
    def get(self, request):
        try : 
            user = User.objects.select_related('author').get(id=request.user.id)

            result = {
                "id"              : user.id,
                "name"            : user.name,
                "description"     : user.introduction,
                "avatar"          : user.thumbnail,
                "subscriber"      : user.subscription.all().count(),
                "interestedAuthor": user.interestedauthor_set.all().count(),
                "author"          : {
                    "description" : user.author.introduction if user.author else None,
                    "career"      : user.author.career if user.author else None
                    }
                }
            return JsonResponse({"result":result}, status = 200)

        except User.DoesNotExist:
            return JsonResponse({"message":"DoesNotExist"}, status = 401)  
        except KeyError:
            return JsonResponse({"message":"KEY ERROR"}, status = 400)    

class ProfileUpdate(View):
    @login_decorator
    def post(self, request):
        name        = request.POST.get('name')
        description = request.POST.get('description')
        image       = request.FILES.get("image")

        extension = image_extension_list
        if not str(image).split('.')[-1] in extension:
            return JsonResponse({"message":"INVALID EXTENSION"}, status = 400)

        user = request.user
        if user.thumbnail.find("amazonaws.com/") != -1:
            file_name = user.thumbnail.split("amazonaws.com/")[-1]
            file_handler.delete(file_name=file_name)

        image_url = file_handler.upload(file=image)
        
        author = Author.objects.filter(user_id = user.id)
        user = User.objects.filter(id = user.id)
        if author.exists():
            user.update(name = name, thumbnail = image_url)
            author.update(introduction = description)
            return JsonResponse({"message":"SUCCESS"}, status = 201)

        user.update(
                name         = name,
                thumbnail    = image_url,
                introduction = description
                )
        return JsonResponse({"message":"SUCCESS"}, status = 201)
            