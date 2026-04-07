from django.contrib.auth.mixins import UserPassesTestMixin

from bugbox3.core.permissions import IS_RESEARCH, user_has_morphospecies_research_or_reviewer_access


class MorphospeciesResearchOrReviewerMixin(UserPassesTestMixin):
    """Allow full researchers OR taxonomy reviewers (minimal morphospecies perms)."""

    def test_func(self):
        return user_has_morphospecies_research_or_reviewer_access(self.request.user)


class MorphospeciesResearchOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.has_perms(IS_RESEARCH)
