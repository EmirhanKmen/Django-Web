from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future). Filter by category and search query if provided.
        """
        queryset = Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")
        
        # Kategori filtreleme
        category = self.request.GET.get('category')
        if category and category != 'Tümü':
            queryset = queryset.filter(category=category)
        
        # Arama filtreleme
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(question_text__icontains=search_query) |
                Q(category__icontains=search_query)
            )
        
        return queryset[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Tüm kategorileri context'e ekle
        context['categories'] = {choice[0]: choice[1] for choice in Question.CATEGORY_CHOICES}
        context['selected_category'] = self.request.GET.get('category', 'Tümü')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = context['question']
        # Maksimum oy sayısını hesapla
        max_votes = max([choice.votes for choice in question.choice_set.all()], default=1)
        context['max_votes'] = max(max_votes, 1)  # Minimum 1 olsun, böylece division by zero olmaz
        return context


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
