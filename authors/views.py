import json

from django.views           import View
from django.http            import JsonResponse

from utils.google_email_api import GoogleEmail
from utils.login_decorator  import login_decorator

from authors.models         import Author, Proposal, ProposalObject

class ProposalView(View):
    @login_decorator
    def post(self, request, author_id):
        try:
            data               = json.loads(request.body)
            content            = data["content"]
            sender_email       = data["sender_email"]
            proposal_object_id = data["proposal_object_id"]
            author             = Author.objects.get(id=author_id)

            google_email = GoogleEmail()
            google_email.generate_token(token_file_path="token.json", credentials_file_path="credentials.json")
            google_email.send_email(content = content, author = author, sender_email = sender_email)

            Proposal.objects.create(
                sender_email       = sender_email,
                content            = content,
                proposal_object_id = proposal_object_id,
                author_id          = author.id,
                user_id            = request.user.id
            )
            return JsonResponse({"message" : "SUCCESS"}, status=201)

        except ProposalObject.DoesNotExist:
            return JsonResponse({"message" : "NO_PROPOSAL_OBJECT"}, status=400)

class AuthorListView(View):
    def get(self, request):
        subcategory = request.GET.get("subcategory")
        authors     = Author.objects.select_related('user','subcategory').filter(subcategory_id = subcategory)
        
        result = [{
            "author_id"          : author.id,
            'author_name'        : author.user.name,
            "author_thumbnail"   : author.user.thumbnail,
            "author_introduction": author.introduction,
            "author_subcategory" : author.subcategory.name,
        }for author in authors]

        return JsonResponse({"result" : result}, status=201)

class AuthorDetailView(View):
    def get(self, request, author_id):
        try:
            authors = Author.objects.select_related('user').get(id = author_id)
            result = {
                "id"              : authors.id,
                "name"            : authors.user.name,
                "description"     : authors.introduction,
                "avatar"          : authors.user.thumbnail,
                "subscriber"      : authors.user.subscription.all().count(),
                "interestedAuthor": authors.user.interestedauthor_set.all().count(),
                }

            return JsonResponse({"result" : result}, status = 200)

        except Author.DoesNotExist:
            return JsonResponse({"message":"DoesNotExist"}, status = 401)  