import json, jwt

from django.test     import TestCase, Client
from django.conf     import settings
from django.db       import transaction

from unittest.mock   import patch

from users.models    import User, SocialAccount
from authors.models  import Author, ProposalObject, Proposal
from contents.models import SubCategory, MainCategory


class ProposalTest(TestCase):
    def setUp(self):
        User.objects.create(
            id           = 1,
            email        = "dno06103@naver.com",
            name         = "김민정",
            thumbnail    = "저거.png",
            introduction = "블라블라블라블라",
        )
        MainCategory.objects.create(
            id   = 1,
            name = "출판"
        )
        SubCategory.objects.create(
            id              = 1,
            name            = "출판기고",
            maincategory_id = 1
        )
        Author.objects.create(
            id             = 1,
            introduction   = "블라블라",
            career         = "블라블라블라블라",
            user_id        = 1,
            subcategory_id = 1
        )
        ProposalObject.objects.create(
            id   = 1,
            name = "출판기고",
        )
        self.token = jwt.encode({'id':User.objects.get(id=1).id}, settings.SECRET_KEY, settings.ALGORITHM)

    def tearDown(self):
        Author.objects.all().delete()
        User.objects.all().delete()
        Proposal.objects.all().delete()
        ProposalObject.objects.all().delete()

    @patch("utils.google_email_api.GoogleEmail")
    def test_success_proposalview_post(self, mocked_requests):
        client = Client()
        data = {
            "content"           : "블라블라",
            "sender_email"      : "dno06101@naver.com",
            "proposal_object_id": 1
        }
        headers = {"HTTP_Authorization":self.token}
        class MockedResponse:
            def __init__(self):
                self.credentials = {}
            def generate_token(self, token_file_path, credentials_file_path):
                return None
            def send_email(self, content, author, sender_email):
                return  {'id': '181771428a3c3f2b', 'threadId': '181771428a3c3f2b', 'labelIds': ['SENT']}
        mocked_requests.return_value = MockedResponse()
        response = client.post('/authors/1/proposal', json.dumps(data), content_type='application/json', **headers)
        self.assertEqual(response.status_code, 201)
    
    @patch("utils.google_email_api.GoogleEmail")
    def test_fail_proposalview_post(self, mocked_requests):
        client = Client()
        data = {
            "content"           : "블라블라",
            "sender_email"      : "dno06101@naver.com",
            "proposal_object_id": 2
        }
        self.token = jwt.encode({'id':1}, settings.SECRET_KEY, settings.ALGORITHM)
        headers = {"HTTP_Authorization":self.token}

        class MockedResponse:
            def __init__(self):
                self.credentials = {}
            def generate_token(self, token_file_path, credentials_file_path):
                return None
            def send_email(self, content, author, sender_email):
                return  {'id': '181771428a3c3f2b', 'threadId': '181771428a3c3f2b', 'labelIds': ['SENT']}

        mocked_requests.return_value = MockedResponse()
        response = client.post('/authors/1/proposal', json.dumps(data), content_type='application/json', **headers)
        self.assertEqual(response.status_code, 400)

class AuthorListViewTest(TestCase):
    def setUp(self):
        with transaction.atomic():
            User.objects.bulk_create([
                User(
                    id           = 1,
                    name         = "홍길동",
                    email        = "test@gmail.com",
                    thumbnail    = "test.jpg",
                    introduction = "홍길동님의 BranchTime입니다."
                    ),
                User(
                    id           = 2,
                    name         = "김길동",
                    email        = "test1@gmail.com",
                    thumbnail    = "test1.jpg",
                    introduction = "김길동님의 BranchTime입니다."
                    )
                ])
            SocialAccount.objects.bulk_create([
                SocialAccount(
                    id                = 1,
                    social_account_id = "123123123",
                    name              = "kakao",
                    user_id           = 1
                    ),
                SocialAccount(
                    id                = 2,
                    social_account_id = "123123456",
                    name              = "kakao",
                    user_id           = 2
                    ) 
                ])
        MainCategory.objects.create(
            id   = 1,
            name = "메인카테고리"
        )
        SubCategory.objects.create(
            id              = 1,
            name            = "서브카테고리",
            maincategory_id = 1
        )

        Author.objects.create(
            id             = 1,
            introduction   = "나는 작가 홍길동입니다",
            career         = "한국대학교 졸업",
            user_id        = 1,
            subcategory_id = 1
        )
        

    def tearDown(self):
        User.objects.all().delete()
        MainCategory.objects.all().delete()
        SubCategory.objects.all().delete()
        Author.objects.all().delete()

    def test_author_list_view(self):
        client = Client()

        response = client.get('/authors/list?subcategory=1', content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {
            "result": [{
                "author_id"           : 1,
                "author_name"         : "홍길동",
                "author_thumbnail"    : "test.jpg",
                "author_introduction": "나는 작가 홍길동입니다",
                "author_subcategory"  : "서브카테고리",
                }]
            }
        )
