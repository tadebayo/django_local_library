from django.shortcuts import render
from .models import Author, Book, BookInstance, Genre

# Create your views here.

def index(request):
	"""
	View function for home page site.
	"""
	num_books = Book.objects.all().count()
	num_authors = Author.objects.all().count()
	num_bookinstances = BookInstance.objects.all().count()
	num_instances_available = BookInstance.objects.filter(status__exact='a').count()
	num_genre = Genre.objects.all().count()
	num_books_containthe = Book.objects.filter(title__icontains='the').count

	num_visits = request.session.get('num_visits', 0)
	request.session['num_visits'] = num_visits + 1

	return render(request, 'index.html', context={'num_books':num_books,'num_authors':num_authors,'num_bookinstances':num_bookinstances,'num_instances_available':num_instances_available, 'num_genre':num_genre, 'num_books_containthe':num_books_containthe, 'num_visits':num_visits})



from django.views import generic
class BookListView(generic.ListView):
	model = Book
	paginate_by = 2


class BookDetailView(generic.DetailView):
	model = Book

class AuthorListView(generic.ListView):
	model = Author
	paginate_by = 10

class AuthorDetailView(generic.DetailView):
	model = Author 


from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
	model = BookInstance
	template_name = 'catalog/bookinstance_list_borrowed_user.html'
	paginate_by = 3

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

from django.contrib.auth.mixins import PermissionRequiredMixin

class AllBorrowedBooksListView(PermissionRequiredMixin,generic.ListView):
	permission_required = 'catalog.can_mark_returned'
	model = BookInstance
	template_name = 'catalog/bookinstance_list_allborrowed_books.html'
	paginate_by = 3

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact='o').order_by('due_back')






from django.contrib.auth.decorators import permission_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import datetime

from .forms import RenewBookForm, RenewBookModelForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    View function for renewing a specific BookInstance by librarian
    """
    book_inst=get_object_or_404(BookInstance, pk = pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
       #form = RenewBookForm(request.POST)
       form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
       if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
           # book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.due_back = form.cleaned_data['due_back']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Book

class BookCreate(CreateView):
    model = Book
    fields = '__all__'
   

class BookUpdate(UpdateView):
    model = Book 
    fields = '__all__'

class BookDelete(DeleteView):
    model = Book 
    success_url = reverse_lazy('books')
