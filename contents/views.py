import datetime

from django.views          import View
from django.http           import JsonResponse
from django.shortcuts      import get_object_or_404

from utils.login_decorator import login_decorator
from contents.models       import Post, SubCategory, User, Comment, PostLike, MainCategory


class CategoryView(View):
    def get(self, request):
        categoris = MainCategory.objects.all().prefetch_related('subcategory_set')

        result = [{
            "maincategory_id"  : category.id,
            "maincategory_name": category.name,
            "subcategory_list":[{
                "subcategory_id"  : sub.id,
                "subcategory_name": sub.name,
                }for sub in category.subcategory_set.all() ]
                } for category in categoris]

        return JsonResponse({'result' : result }, status=200)

class CommentUploadView(View):
    @login_decorator
    def post(self, request, post_id):
        try:
            content         = request.POST["content"]
            user            = request.user
            image           = request.FILES['comment_image']

            if not str(image).split('.')[-1] in ['png', 'jpg', 'gif', 'jpeg']:
                return JsonResponse({"message" : "INVALID EXTENSION"}, status=400)

            key = "comment_image/" + str(post_id) + "/" + str(image) 

            upload_fileobj(Fileobj=image, Bucket=bucket, Key=key, ExtraArgs=args)

            image_url = MEDIA_URL + key

            Comment.objects.create(
                content = content,
                user_id = user.id,
                image   = image_url,
                post_id = post_id
            )

            return JsonResponse({'message' : "SUCCESS"}, status=201)

        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)
            
class PostUploadView(View):
    @login_decorator
    def get(self, request):
        try:
            categories = MainCategory.objects.prefetch_related('subcategory_set').all()

            results = [{
                'id'  : category.id,
                'main_category_name': category.name,
                'sub_category' : [{
                    'id': subcategory.id,
                    'name': subcategory.name
                }for subcategory in category.subcategory_set.all()]
            } for category in  categories]

            return JsonResponse({'message' : results }, status=200)

        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)
        
    @login_decorator
    def post(self, request):
        try:
            content         = request.POST["content"]
            reading_time    = datetime.time(0,int(len(content.replace(" ",""))/275+1),0)
            user            = request.user
            subcategory     = request.POST["subcategory"]
            sub_title       = request.POST["sub_title"]
            thumbnail_image = request.FILES.get('thumbnail_image', None)
            color_code      = request.POST.get('color_code', None)
            title           = request.POST["title"]

            if thumbnail_image is not None:
                if not str(thumbnail_image).split('.')[-1] in ['png', 'jpg', 'gif', 'jpeg']:
                    return JsonResponse({"message" : "INVALID EXTENSION"}, status=400)

                key = "/thumbnail_image/" + str(user.id) + "/" + str(thumbnail_image) 

                upload_fileobj(Fileobj=thumbnail_image, Bucket=bucket, Key=key, ExtraArgs=args)
                thumbnail_image = MEDIA_URL + key

            else:
                thumbnail_image = color_code

            Post.objects.create(
                content         = content,
                user_id         = user.id,
                subcategory_id  = SubCategory.objects.get(id=subcategory).id,
                sub_title       = sub_title,
                thumbnail_image = thumbnail_image,
                title           = title,
                reading_time    = reading_time,
            )

            return JsonResponse({'message' : "SUCCESS"}, status=201)

        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)

class PostView(View):
    def get(self, request, post_id):
        try:
            results = []
            post = Post.objects.prefetch_related('postlike_set','comment_set').select_related('user','subcategory').get(id = post_id)
            comments = post.comment_set.all()
            comment = [{
                'user_name'      : comment.user.name,
                'comment_image'  : comment.image,
                'comment_content': comment.content,
                'comment_id'     : comment.id
            } for comment in comments]
            
            results.append({
                'comment_information'    : comment,
                'post_title'             : post.title,
                'post_subtitle'          : post.sub_title,
                'post_subcategory_name'  : post.subcategory.name,
                'post_user_name'         : post.user.name,
                'post_created_at'        : post.created_at.strftime("%b.%d.%Y"),
                'post_content'           : post.content,
                'post_like_count'        : post.postlike_set.count(),
                'post_thumbnail_image'   : post.thumbnail_image,
                'user_name'              : post.user.name,
                'user_thumbnail'         : post.user.thumbnail,
                'user_introduction'      : post.user.introduction,
                'user_subscription_count': post.user.subscription.all().count(),
                'post_id'                : post.id
            })

            return JsonResponse({'message' : results }, status=200)

        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)

class ContentImageUploadView(View):
    @login_decorator
    def post(self, request):
        try:
            content_image = request.FILES['content_image']
            print(content_image)
            if not str(content_image).split('.')[-1] in ['png', 'jpg', 'gif', 'jpeg']:
                return JsonResponse({"message" : "INVALID EXTENSION"}, status=400)

            key = "content_image/" + str(request.user.id) + "/" + str(content_image)

            upload_fileobj(Fileobj=content_image, Bucket=bucket, Key=key, ExtraArgs=args)

            bucket_object_name = MEDIA_URL + key
            
            return JsonResponse({'message' : bucket_object_name}, status=201)

        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)

class CommentView(View):
    @login_decorator
    def post(self, request, comment_id):
        try:
            content = request.POST.get('content', None)
            image   = request.FILES.get('image', None)
            comment = get_object_or_404(Comment, id=comment_id)

            if image is not None:
                KEY = comment.image.split("amazonaws.com/")[-1]
                key = str(KEY) 
                delete_object(Bucket = bucket, Key=key)
           
                key = "comment_image/" + str(comment.post_id) + "/" + str(image) 
                print(key)
                upload_fileobj(Fileobj = image, Bucket=bucket, Key=key, ExtraArgs=args)
            
                image_url     = MEDIA_URL + key
                comment.image = image_url

            if content is not None:
                comment.content = content

            comment.save()

            return JsonResponse({'message' : "SUCCESS"}, status=200)

        except KeyError :
                return JsonResponse({"message" : "KEY_ERROR"}, status=400)


    @login_decorator
    def delete(self, request, comment_id):
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            comment.delete()

            return JsonResponse({'message' : "SUCCESS"}, status=204)

        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)



class PostListView(View):
    def get(self, request, maincategory_id):
        try:
            main = MainCategory.objects.get(id = maincategory_id)
            subcategory_lists = main.subcategory_set.all()
            list ={ 
                "title_list":{
                    "main_id"  : main.id,
                    "main_title": main.name
                    },
                "sub_title":[{
                    "sub_id"  : subcategory_list.id,
                    "sub_title": subcategory_list.name,
                    } for subcategory_list in subcategory_lists],
                "post_list":[[{
                    "post_id"      : post.id,
                    "post_title"   : post.title,
                    "post_subTitle": post.sub_title,
                    "desc"         : post.content,
                    "commentCount" : post.comment_set.all().count(),
                    "writeTime"    : post.reading_time,
                    "writeUser"    : post.user.name,
                    "imgSrc"       : post.thumbnail_image,
                    } for post in Post.objects.select_related("user").filter(subcategory_id=subcategory_list.id)] for subcategory_list in subcategory_lists]
                    }
            
            return JsonResponse({"post_list":list}, status = 200)

        except MainCategory.DoesNotExist:
            return JsonResponse({"message":"DoesNotExist"}, status = 401)  
        
        except KeyError:
            return JsonResponse({"message":"KEY ERROR"}, status = 400)        
