from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Activation
from simulation.models import Election, Candidate


class IndexPageView(LoginRequiredMixin, TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_users = Activation.objects.filter(user_id = self.request.user.id)
        if(len(active_users)):
            context['voting_allowed'] = Activation.objects.filter(user_id = self.request.user.id)[0].voting_allowed
            context['election'] = Election.objects.filter(is_open = True).first()
            context['closed_election'] = Election.objects.filter(is_open = False).first()
        return context

class TOTPPageView(LoginRequiredMixin, TemplateView):
    template_name = 'main/2fa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['private_key'] = Activation.objects.filter(user_id = self.request.user.id)[0].private_key_ecc
        private_key_ecc = Activation.objects.filter(user_id = self.request.user.id)[0]
        private_key_ecc.private_key_ecc = 'PRIVATE'
        private_key_ecc.save()
        return context

class ChangeLanguageView(TemplateView):
    template_name = 'main/change_language.html'
