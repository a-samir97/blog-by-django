from django import forms
from tinymce import TinyMCE
from .models import Post, Comment

class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self,*args):
        return False


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required':False, 'col':30, 'row':10}
        )
    )

    class Meta:
        model = Post
        fields = ('title','overview','content','post_pic','categories','featured','previous_post','next_post')

class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class':'form-control',
        'placeholder':'type your comment',
        'id':'usercomment',
        'rows':'4'
        }))
    class Meta:
        model = Comment
        fields = ('content',)