from django.contrib.auth.mixins import UserPassesTestMixin

from bugbox3.core.permissions import user_has_specimen_research_or_reviewer_access


class SpecimenResearchOrReviewerMixin(UserPassesTestMixin):
    """Allow full researchers OR specimen reviewers"""

    def test_func(self):
        return user_has_specimen_research_or_reviewer_access(self.request.user)
