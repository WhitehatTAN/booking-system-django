from django import forms
from allauth.account.forms import SignupForm
# On importe le validateur spécialisé
from disposable_email_checker.validators import validate_disposable_email

class CustomSignupForm(SignupForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # On essaie de valider l'email avec la librairie
        try:
            validate_disposable_email(email)
        except forms.ValidationError:
            # Si la librairie détecte un email jetable, elle lève une erreur
            # On la capture pour afficher notre propre message en français
            raise forms.ValidationError("Les adresses temporaires ne sont pas acceptées. Veuillez utiliser une vraie adresse.")
            
        return email