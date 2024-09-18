# coding=utf8
from django import forms
from .models import Question, Tag


class MultiTagField(forms.CharField):
    def to_python(self, value):
        if not value:
            return []
        return [item.strip() for item in value.split(',')]


class QuestionForm(forms.ModelForm):
    tags = MultiTagField(required=False, max_length=200)

    class Meta:
        model = Question
        fields = ['title', 'text']

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', [])
        if len(tags) > 3:
            raise forms.ValidationError('Количество тегов должно быть не более трех.')
        return tags

    def save(self, commit=True):
        question = super(QuestionForm, self).save(commit=commit)

        if commit:
            tags_list = self.cleaned_data['tags']
            question.tags.clear()
            for tag_name in tags_list:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)

        return question
