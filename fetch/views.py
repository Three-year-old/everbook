from django.shortcuts import render


def search(request):
    print(request.GET.get('q'))
    return render(request, 'index.html', {
        'q': request.GET.get('q')
    })
