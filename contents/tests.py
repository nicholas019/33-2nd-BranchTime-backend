import jwt, uuid

from django.test                    import TestCase, Client
from django.conf                    import settings
from django.db                      import transaction

from unittest.mock                  import patch
from django.core.files.uploadedfile import SimpleUploadedFile

from users.models                   import User, SocialAccount
from .models                        import MainCategory, SubCategory, Post, Comment


class CategoryViewTest(TestCase):
    def setUp(self):
        MainCategory.objects.bulk_create([
            MainCategory(id = 1, name = "메인카테고리1"),
            MainCategory(id = 2, name = "메인카테고리2"),
        ])
        SubCategory.objects.bulk_create([
            SubCategory(id = 1, name = "서브카테고리1", maincategory_id = 1,),
            SubCategory(id = 2, name = "서브카테고리2", maincategory_id = 1,),
            SubCategory(id = 3, name = "서브카테고리3", maincategory_id = 1,),
            SubCategory(id = 4, name = "서브카테고리4", maincategory_id = 2,),
            SubCategory(id = 5, name = "서브카테고리5", maincategory_id = 2,),
            SubCategory(id = 6, name = "서브카테고리6", maincategory_id = 2,),
        ])
    def tearDown(self):
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()

    def test_success_category_list_view(self):
        client = Client()    

        response = client.get('/contents/category')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "result": [{
                "maincategory_id": 1,
                "maincategory_name": "메인카테고리1",
                "subcategory_list": [
                    {
                        "subcategory_id": 1,
                        "subcategory_name": "서브카테고리1"
                    },
                    {
                        "subcategory_id": 2,
                        "subcategory_name": "서브카테고리2"
                    },
                    {
                        "subcategory_id": 3,
                        "subcategory_name": "서브카테고리3"
                    }]},
                {
                        "maincategory_id": 2,
                        "maincategory_name": "메인카테고리2",
                        "subcategory_list": [
                    {
                        "subcategory_id": 4,
                        "subcategory_name": "서브카테고리4"
                    },
                    {
                        "subcategory_id": 5,
                        "subcategory_name": "서브카테고리5"
                    },
                    {
                        "subcategory_id": 6,
                        "subcategory_name": "서브카테고리6"
                    }]}
                    ]})

class PostListViewTest(TestCase):
    def setUp(self):
        with transaction.atomic():
            User.objects.create(
                id           = 1,
                name         = "홍길동",
                email        = "test@gmail.com",
                thumbnail    = "test.jpg",
                introduction = "홍길동님의 BranchTime입니다."
            )
            SocialAccount.objects.create(
                        id                = 1,
                        social_account_id = "123123123",
                        name              = "kakao",
                        user_id           = 1
                        )
        
        MainCategory.objects.bulk_create([
            MainCategory(id = 1, name = "메인카테고리1"),
            MainCategory(id = 2, name = "메인카테고리2"),
            MainCategory(id = 3, name = "메인카테고리3"),
        ])
        SubCategory.objects.bulk_create([
            SubCategory(id = 1, name = "서브카테고리1", maincategory_id = 1,),
            SubCategory(id = 2, name = "서브카테고리2", maincategory_id = 1,),
            SubCategory(id = 3, name = "서브카테고리3", maincategory_id = 1,),
        ])
        Post.objects.bulk_create([
            Post(
                id              = 1,
                title           = "1번글 제목입니다",
                sub_title       = "1번 소제목입니다",
                thumbnail_image = "test.jpg",
                content         = "1번글 내용",
                reading_time    = "13:10",
                subcategory_id  = 1,
                user_id         = 1
            ),
            Post(
                id              = 2,
                title           = "2번글 제목입니다",
                sub_title       = "2번 소제목입니다",
                thumbnail_image = "test.jpg",
                content         = "2번글 내용",
                reading_time    = "13:10",
                subcategory_id  = 2,
                user_id         = 1
            ),
            Post(
                id              = 3,
                title           = "3번글 제목입니다",
                sub_title       = "3번 소제목입니다",
                thumbnail_image = "test.jpg",
                content         = "3번글 내용",
                reading_time    = "13:10",
                subcategory_id  = 3,
                user_id         = 1
            )
        ])
        
    def tearDown(self):
        MainCategory.objects.all().delete()  
        SubCategory.objects.all().delete()  
        Post.objects.all().delete()  

    def test_post_list_view_success(self):
        client = Client()        

        response = client.get('/contents/postlist?maincategory=1&subcategory=1', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "result":[{
                "maincategory_id": 1,
                "subcategory_id" : 1,
                "post_id"        : 1,
                "post_title"     : "1번글 제목입니다",
                "post_subTitle"  : "1번 소제목입니다",
                "desc"           : "1번글 내용",
                "commentCount"   : 0,
                "writeTime"      : "Jul.04.2022",
                "writeUser"      : "홍길동",
                "imgSrc"         : "test.jpg",
            }]
        })

class PostUploadViewTest(TestCase):
    def setUp(self):
        with transaction.atomic():
            User.objects.create(
                id           = 1,
                name         = "홍길동",
                email        = "test@gmail.com",
                thumbnail    = "test.jpg",
                introduction = "홍길동님의 BranchTime입니다."
            )
            SocialAccount.objects.create(
                        id                = 1,
                        social_account_id = "123123123",
                        name              = "kakao",
                        user_id           = 1
                        )
        MainCategory.objects.create(
                id   = 1,
                name = "메인카테고리"
            )
        SubCategory.objects.create(
                id              = 1,
                name            = "서브카테고리",
                maincategory_id = 1
            )                
    def tearDown(self):
        User.objects.all().delete()
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()

    @patch("utils.fileuploader_api.FileUploader.upload")
    def test_success_post_upload(self, mocked_requests):
        client = Client()
        self.token = jwt.encode({'id':1}, settings.SECRET_KEY, settings.ALGORITHM)
        headers    = {"HTTP_Authorization":self.token}
        image      = SimpleUploadedFile('python.png', b'')

        class MockedResponse:
            def upload(file):
                file   = str(uuid.uuid4())
                config = settings.AWS_STORAGE_BUCKET_NAME
                return f'https://{config}.s3.{settings.AWS_REGION}.amazonaws.com/{file}'

        mocked_requests.return_value = MockedResponse()
        data = {
            "title" : "제목1",
            "sub_title" : "소제목1",
            "image" : image,
            "content" : "글내용1",
            "subcategory_id" : 1
        }
        response = client.post("/contents/postupload", data, **headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),{"message":"SUCCESS"})

class PostDetailViewTest(TestCase):
    def setUp(self):
        with transaction.atomic():
            User.objects.create(
                id           = 1,
                name         = "홍길동",
                email        = "test@gmail.com",
                thumbnail    = "test.jpg",
                introduction = "홍길동님의 BranchTime입니다."
            )
            SocialAccount.objects.create(
                        id                = 1,
                        social_account_id = "123123123",
                        name              = "kakao",
                        user_id           = 1
                        )
        MainCategory.objects.create(
                id   = 1,
                name = "메인카테고리"
            )
        SubCategory.objects.create(
                id              = 1,
                name            = "서브카테고리",
                maincategory_id = 1
            )  
        Post.objects.create(
            id = 1,
            title = "제목1",
            sub_title = "소제목1",
            thumbnail_image = "test.png",
            content = "내용1",
            reading_time = "01:01",
            user_id = 1,
            subcategory_id = 1
            )
        Comment.objects.create(
            id = 1,
            image = "test1.png",
            content = "댓글1",
            post_id = 1,
            user_id = 1
        )      
    def tearDown(self):
        User.objects.all().delete()
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()
        Post.objects.all().delete()
        Comment.objects.all().delete()

    def test_post_detail_view(self):
        client = Client()

        response = client.get('/contents/post/1', content_type='application/json')
        self.assertEqual(response.status_code, 200)

class CommentUploadViewTest(TestCase):
    def setUp(self):
        with transaction.atomic():
            User.objects.create(
                id           = 1,
                name         = "홍길동",
                email        = "test@gmail.com",
                thumbnail    = "test.jpg",
                introduction = "홍길동님의 BranchTime입니다."
            )
            SocialAccount.objects.create(
                        id                = 1,
                        social_account_id = "123123123",
                        name              = "kakao",
                        user_id           = 1
                        )
        MainCategory.objects.create(
                id   = 1,
                name = "메인카테고리"
            )
        SubCategory.objects.create(
                id              = 1,
                name            = "서브카테고리",
                maincategory_id = 1
            )  
        Post.objects.create(
            id = 1,
            title = "제목1",
            sub_title = "소제목1",
            thumbnail_image = "test.png",
            content = "내용1",
            reading_time = "01:01",
            user_id = 1,
            subcategory_id = 1
            )
        self.token = jwt.encode({'id':1}, settings.SECRET_KEY, settings.ALGORITHM)
    
    def tearDown(self):
        User.objects.all().delete()
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()
        Post.objects.all().delete()

    @patch("utils.fileuploader_api.FileUploader.upload")
    def test_commnet_upload_view(self, mocked_requests):            
        client = Client()
        headers    = {"HTTP_Authorization":self.token}
        image      = SimpleUploadedFile('python.png', b'')

        class MockedResponse:
            def upload(file):
                file = str(uuid.uuid4())
                config = settings.AWS_STORAGE_BUCKET_NAME
                return f'https://{config}.s3.{settings.AWS_REGION}.amazonaws.com/{file}'
        
        data = {
            "image" : image,
            "content" : "댓글1"
        }
        mocked_requests.return_value = MockedResponse()
        response = client.post("/contents/post/1/comment", data, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{"message":"SUCCESS"})


class CommentUpdateViewTest(TestCase):
    def setUp(self):
        with transaction.atomic():
            User.objects.create(
                id           = 1,
                name         = "홍길동",
                email        = "test@gmail.com",
                thumbnail    = "test.jpg",
                introduction = "홍길동님의 BranchTime입니다."
            )
            SocialAccount.objects.create(
                        id                = 1,
                        social_account_id = "123123123",
                        name              = "kakao",
                        user_id           = 1
                        )
        MainCategory.objects.create(
                id   = 1,
                name = "메인카테고리"
            )
        SubCategory.objects.create(
                id              = 1,
                name            = "서브카테고리",
                maincategory_id = 1
            )  
        Post.objects.create(
            id = 1,
            title = "제목1",
            sub_title = "소제목1",
            thumbnail_image = "test.png",
            content = "내용1",
            reading_time = "01:01",
            user_id = 1,
            subcategory_id = 1
            )
        Comment.objects.create(
            id = 1,
            image = "test1.png",
            content = "댓글1",
            post_id = 1,
            user_id = 1
        )          
        self.token = jwt.encode({'id':1}, settings.SECRET_KEY, settings.ALGORITHM)
    
    def tearDown(self):
        User.objects.all().delete()
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()
        Post.objects.all().delete()

    @patch("utils.fileuploader_api.FileUploader.upload")
    def test_commnet_update_view(self, mocked_requests):            
        client  = Client()
        headers = {"HTTP_Authorization":self.token}
        image   = SimpleUploadedFile('django.png', b'')

        class MockedResponse:
            def upload(file):
                file = str(uuid.uuid4())
                config = settings.AWS_STORAGE_BUCKET_NAME
                return f'https://{config}.s3.{settings.AWS_REGION}.amazonaws.com/{file}'
        
        data = {
            "image" : image,
            "content" : "댓글수정1"
        }
        mocked_requests.return_value = MockedResponse()
        response = client.post("/contents/post/1/comment/1", data, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{"message":"SUCCESS"})

    @patch("utils.fileuploader_api.FileUploader.delete")
    def test_commnet_delete_view(self, mocked_requests):            
        client  = Client()
        headers = {"HTTP_Authorization":self.token}
        
        class MockedResponse:
            def delete(file_name):
                file_name = 1231289
                pass
        
        mocked_requests.return_value = MockedResponse()
        response = client.delete("/contents/post/1/comment/1", **headers)
        self.assertEqual(response.status_code, 204)
