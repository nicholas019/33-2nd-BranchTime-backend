import json, jwt

from django.test        import TestCase, Client
from django.conf        import settings

from unittest.mock      import patch

from authors.models     import Author, User, ProposalObject, Proposal
from contents.models    import SubCategory, MainCategory


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
