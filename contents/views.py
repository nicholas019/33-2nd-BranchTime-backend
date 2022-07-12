import datetime, boto3

from django.views           import View
from django.http            import JsonResponse
from django.db.models       import Q
from django.conf            import settings
from django.shortcuts       import get_object_or_404

from utils.login_decorator  import login_decorator
from utils.fileuploader_api import FileUploader, FileHandler, image_extension_list
from contents.models        import Post, Comment, MainCategory
config = {
    "bucket" : settings.AWS_STORAGE_BUCKET_NAME
}
file_uploader = FileUploader(boto3.client('s3'), config)
file_handler = FileHandler(file_uploader)

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

class PostListView(View):
    def get(self, request):
        try:
            maincategory_id = request.GET.get('maincategory')
            subcategory_id  = request.GET.get('subcategory')

            q=Q()
            if maincategory_id:
                q &= Q(subcategory__maincategory_id= maincategory_id)

            if subcategory_id:
                q &= Q(subcategory__id= subcategory_id)

            posts =Post.objects.filter(q).select_related('subcategory', 'user').order_by("-id")

            result = [{
                "maincategory_id": post.subcategory.maincategory_id,
                "subcategory_id" : post.subcategory_id,
                "post_id"        : post.id,
                "post_title"     : post.title,
                "post_subTitle"  : post.sub_title,
                "desc"           : post.content,
                "commentCount"   : post.comment_set.all().count(),
                "writeTime"      : post.created_at.strftime("%b.%d.%Y"),
                "writeUser"      : post.user.name,
                "imgSrc"         : post.thumbnail_image,
                } for post in posts]
                    
            return JsonResponse({'result' : result }, status=200)
        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)

class PostImageUpload(View):
    def post(self, request):
        image = request.FILES['image']
        
        extension = image_extension_list
        if not str(image).split('.')[-1] in extension:
            return JsonResponse({"message":"INVALID EXTENSION"}, status = 400)
        
        image_url = file_handler.upload(file=image)
        
        return JsonResponse({'result' : image_url}, status=201)

class PostUploadView(View):
    @login_decorator
    def post(self, request):
        try:
            title          = request.POST["title"]
            sub_title      = request.POST["sub_title"]
            image          = request.FILES.get('image', None)
            color_code     = request.POST.get('color_code', None)
            content        = request.POST["content"]
            reading_time   = datetime.time(0,int(len(content.replace(" ",""))/275+1),0)
            subcategory_id = request.POST["subcategory_id"]
            
            if image:
                extension = ['PNG', 'png','jpg', 'JPG', 'GIF', 'gif', 'JPEG', 'jpeg']
                if not str(image).split('.')[-1] in extension:
                    return JsonResponse({"message":"INVALID EXTENSION"}, status = 400)

                image_url = file_handler.upload(file=image)
            else:
                image_url = color_code

            Post.objects.create(
                title           = title,
                sub_title       = sub_title,
                thumbnail_image = image_url,
                content         = content,
                reading_time    = reading_time,
                user_id         = request.user.id,
                subcategory_id  = subcategory_id,
            )

            return JsonResponse({"message":"SUCCESS"}, status=201)

        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)

class PostDetailView(View):
    def get(self, request, post_id):
        try:
            results = []
            post = Post.objects.prefetch_related('postlike_set','comment_set').select_related('user','subcategory').get(id = post_id)
            comments = post.comment_set.all()
            comment = [{
                'comment_id'     : comment.id,
                'user_name'      : comment.user.name,
                'comment_image'  : comment.image,
                'comment_content': comment.content,
            } for comment in comments]
            
            results.append({
                'post_id'                : post.id,
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
                'comment_information'    : comment,
            })

            return JsonResponse({'result' : results }, status=200)

        except KeyError :
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)

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