from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render

from leagues.models import Description, Contestants, Results
from leagues.forms import DescriptionForm, ContestantsForm, ResultsForm, UploadForm, RequiredFormSet, Required2FormSet
from leagues.tools import create_schedule, handle_uploaded_file

from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory

from django.contrib.gis.geoip import GeoIP
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import struct

def index(request):
    last_leagues = Description.objects.all().order_by('-id')[:10]
    user_ip_adress = request.META['REMOTE_ADDR']
    user_country = GeoIP().country_code('%s' % user_ip_adress)
    ContestantsFormSet = formset_factory(ContestantsForm, formset=RequiredFormSet, extra=4, max_num=10)
    
    if request.method == 'POST':
        description_form = DescriptionForm(request.POST)
        contestants_formset = ContestantsFormSet(request.POST)
        teams_num = contestants_formset.total_form_count()
        if description_form.is_valid() and contestants_formset.is_valid() and teams_num >= 4 and teams_num < 21:
            human = True
            
            description = description_form.save(commit=False)
            description.teams = teams_num
            description.country = user_country
            description.save()
            
            # save contestant to list
            team_ids = []
            for form in contestants_formset.forms:
                contestants = form.save(commit=False)
                contestants.league = description
                contestants.save()
                team_ids.append(contestants)
                
            # create pairs and add match
            for round in create_schedule(team_ids, description.rounds):
                for match in round:
                    if match[0] != "BYE" and match[1] != "BYE":
                        add_match = Results(league=description, contestant1=match[0], contestant2=match[1])
                        add_match.save()
                        
            # save league id to cookie
            request.session['league_id'] = description.id
            request.session.set_expiry(3600)
                
            return HttpResponseRedirect(reverse('leagues:detail', args=(description.id,)))
    else:
        description_form = DescriptionForm()
        contestants_formset = ContestantsFormSet()
        teams_num = contestants_formset.total_form_count()
        
    return render(request, 'leagues/index.html', {'description_form': description_form, 'contestants_formset': contestants_formset, 'teams_num': teams_num, 'last_leagues': last_leagues})

def detail(request, league_id):
    league = get_object_or_404(Description, pk=league_id)
    get_results = Results.objects.filter(league=league_id).order_by('id')
    get_contestants = Contestants.objects.extra(select={'diff': 'goal_for - goal_against'}, where=['league_id=%s'], params=[league_id]).order_by('-points', '-diff', 'id')
    can_edit_and_delete = False
    
    if request.session.get('league_id', False) and request.session['league_id'] == int(league_id):
        can_edit_and_delete = True
        
    return render(request, 'leagues/detail.html', {'visible': can_edit_and_delete, 'league': league, 'all_results': get_results, 'all_contestants': get_contestants})

def admin_pass(request, league_id):
    league = get_object_or_404(Description, pk=league_id)
    
    if request.method != 'POST' or 'admin_pass' not in request.POST:
        raise Http404('Only POST method!')
        
    if request.POST['admin_pass'] == league.password:
        request.session['league_id'] = int(league_id)
        request.session.set_expiry(3600)
        
    return HttpResponseRedirect(reverse('leagues:detail', args=(league.id,)))
    
def set_score(request, result_id):
    results = get_object_or_404(Results, pk=result_id)
    
    old_result1 = results.result1
    old_result2 = results.result2
    
    if request.session.get('league_id', False) and request.session['league_id'] == results.league.id:
        if request.method == 'POST':
            form = ResultsForm(request.POST, instance=results)
            if form.is_valid():
                new_result1 = results.result1
                new_result2 = results.result2
                
                if old_result1 and old_result2 < 0:
                    if form.instance.result1 > form.instance.result2:
                        form.instance.contestant1.match += 1
                        form.instance.contestant1.win += 1
                        form.instance.contestant1.goal_for += new_result1
                        form.instance.contestant1.goal_against += new_result2
                        form.instance.contestant1.points += 3
                        form.instance.contestant1.save()
                        
                        form.instance.contestant2.match += 1
                        form.instance.contestant2.loss += 1
                        form.instance.contestant2.goal_for += new_result2
                        form.instance.contestant2.goal_against += new_result1
                        #form.instance.contestant2.points -= 0 - not required
                        form.instance.contestant2.save()
                        
                    elif form.instance.result2 > form.instance.result1:
                        form.instance.contestant2.match += 1
                        form.instance.contestant2.win += 1
                        form.instance.contestant2.goal_for += new_result2
                        form.instance.contestant2.goal_against += new_result1
                        form.instance.contestant2.points += 3
                        form.instance.contestant2.save()
                        
                        form.instance.contestant1.match += 1
                        form.instance.contestant1.loss += 1
                        form.instance.contestant1.goal_for += new_result1
                        form.instance.contestant1.goal_against += new_result2
                        #form.instance.contestant1.points -= 0 - not required
                        form.instance.contestant1.save()
                        
                    elif form.instance.result1 == form.instance.result2:
                        form.instance.contestant1.match += 1
                        form.instance.contestant1.draw += 1
                        form.instance.contestant1.goal_for += new_result1
                        form.instance.contestant1.goal_against += new_result2
                        form.instance.contestant1.points += 1
                        form.instance.contestant1.save()
                        
                        form.instance.contestant2.match += 1
                        form.instance.contestant2.draw += 1
                        form.instance.contestant2.goal_for += new_result2
                        form.instance.contestant2.goal_against += new_result1
                        form.instance.contestant2.points += 1
                        form.instance.contestant2.save()
                        
                else:
                    
                    if old_result1 > old_result2 and new_result1 > new_result2:
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.save()
                        
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.save()
                    elif old_result1 > old_result2 and new_result1 < new_result2:
                        form.instance.contestant1.win -= 1
                        form.instance.contestant1.loss += 1
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.points -= 3
                        form.instance.contestant1.save()
                        
                        form.instance.contestant2.loss -= 1
                        form.instance.contestant2.win += 1
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.points += 3
                        form.instance.contestant2.save()
                    elif old_result1 > old_result2 and new_result1 == new_result2:
                        form.instance.contestant1.win -= 1
                        form.instance.contestant1.draw += 1
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.points -= 2
                        form.instance.contestant1.save()
                        
                        form.instance.contestant2.loss -= 1
                        form.instance.contestant2.draw += 1
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.points += 1
                        form.instance.contestant2.save()
                    
                    
                    if old_result2 > old_result1 and new_result2 > new_result1:
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.save()
                        
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.save()
                    elif old_result2 > old_result1 and new_result2 < new_result1:
                        form.instance.contestant2.win -= 1
                        form.instance.contestant2.loss += 1
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.points -= 3
                        form.instance.contestant2.save()
                        
                        form.instance.contestant1.loss -= 1
                        form.instance.contestant1.win += 1
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.points += 3
                        form.instance.contestant1.save()
                    elif old_result2 > old_result1 and new_result2 == new_result1:
                        form.instance.contestant2.win -= 1
                        form.instance.contestant2.draw += 1
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.points -= 2
                        form.instance.contestant2.save()
                        
                        form.instance.contestant1.loss -= 1
                        form.instance.contestant1.draw += 1
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.points += 1
                        form.instance.contestant1.save()
                    
                    
                    if old_result1 == old_result2 and new_result1 > new_result2:
                        form.instance.contestant1.draw -= 1
                        form.instance.contestant1.win += 1
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.points += 2
                        form.instance.contestant1.save()
                        
                        form.instance.contestant2.draw -= 1
                        form.instance.contestant2.loss += 1
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.points -= 1
                        form.instance.contestant2.save()
                    elif old_result1 == old_result2 and new_result2 > new_result1:
                        form.instance.contestant2.draw -= 1
                        form.instance.contestant2.win += 1
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.points += 2
                        form.instance.contestant2.save()
                        
                        form.instance.contestant1.draw -= 1
                        form.instance.contestant1.loss += 1
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.points -= 1
                        form.instance.contestant1.save()
                    elif old_result1 == old_result2 and new_result2 == new_result1:
                        form.instance.contestant1.goal_for += new_result1 - old_result1
                        form.instance.contestant1.goal_against += new_result2 - old_result2
                        form.instance.contestant1.save()
                        
                        form.instance.contestant2.goal_for += new_result2 - old_result2
                        form.instance.contestant2.goal_against += new_result1 - old_result1
                        form.instance.contestant2.save()
                        
                form.save()
                return HttpResponseRedirect(reverse('leagues:detail', args=(results.league.id,)))
        else:
            form = ResultsForm(initial={'result1': old_result1, 'result2': old_result2}
                                        if old_result1 >= 0 else {})
            
        return render(request, 'leagues/set_score.html', {'form': form, 'results': results})
    else:
        return HttpResponseRedirect(reverse('leagues:detail', args=(results.league.id,)))

def clear_score(request, result_id):
    results = get_object_or_404(Results, pk=result_id)

    if request.session.get('league_id', False) and request.session['league_id'] == results.league.id:
        can_clear_score = True
        if results.result1 >= 0 and results.result2 >= 0:
            if request.method == 'POST':
                if results.result1 > results.result2:
                    results.contestant1.match -= 1
                    results.contestant1.win -= 1
                    results.contestant1.goal_for -= results.result1
                    results.contestant1.goal_against -= results.result2
                    results.contestant1.points -= 3
                    results.contestant1.save()
                
                    results.contestant2.match -= 1
                    results.contestant2.loss -= 1
                    results.contestant2.goal_for -= results.result2
                    results.contestant2.goal_against -= results.result1
                    #results.contestant2.points -= 0 not required
                    results.contestant2.save()
                
                    results.result1 = -1
                    results.result2 = -1
                    results.save()
                elif results.result2 > results.result1:
                    results.contestant2.match -= 1
                    results.contestant2.win -= 1
                    results.contestant2.goal_for -= results.result2
                    results.contestant2.goal_against -= results.result1
                    results.contestant2.points -= 3
                    results.contestant2.save()
                
                    results.contestant1.match -= 1
                    results.contestant1.loss -= 1
                    results.contestant1.goal_for -= results.result1
                    results.contestant1.goal_against -= results.result2
                    #results.contestant1.points -= 0 not required
                    results.contestant1.save()
                
                    results.result1 = -1
                    results.result2 = -1
                    results.save()
                elif results.result1 == results.result2:
                    results.contestant1.match -= 1
                    results.contestant1.draw -= 1
                    results.contestant1.goal_for -= results.result1
                    results.contestant1.goal_against -= results.result2
                    results.contestant1.points -= 1
                    results.contestant1.save()
                
                    results.contestant2.match -= 1
                    results.contestant2.draw -= 1
                    results.contestant2.goal_for -= results.result2
                    results.contestant2.goal_against -= results.result1
                    results.contestant2.points -= 1
                    results.contestant2.save()
                
                    results.result1 = -1
                    results.result2 = -1
                    results.save()
        
                return HttpResponseRedirect(reverse('leagues:detail', args=(results.league.id,)))
                
        else:
            can_clear_score = False
            
        return render(request, 'leagues/clear_score.html', {'can_clear_score': can_clear_score})
    else:
        return HttpResponseRedirect(reverse('leagues:detail', args=(results.league.id,)))

def set_replay(request, result_id):
    results = get_object_or_404(Results, pk=result_id)
    
    if request.session.get('league_id', False) and request.session['league_id'] == results.league.id:
        can_upload_replay = True
        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                replay = request.FILES['replay'].read()
                hbrp = replay[4:4+4]
                hbrp_version = int(struct.unpack('i', replay[0:0+4])[0])
                
                if hbrp == 'HBRP' and hbrp_version > 5:
                    full_replay_name = 'league_'+str(results.id)+'.hbr'
                    handle_uploaded_file(request.FILES['replay'], full_replay_name)
                    results.replay = 1
                    results.save()
                    return HttpResponseRedirect(reverse('leagues:detail', args=(results.league.id,)))
                else:
                    can_upload_replay = False
        else:
            form = UploadForm()
        return render(request, 'leagues/set_replay.html', {'form': form, 'can_upload_replay': can_upload_replay})
    else:
        return HttpResponseRedirect(reverse('leagues:detail', args=(results.league.id,)))

def edit_names(request, league_id):
    league = get_object_or_404(Description, pk=league_id)
    
    if request.session.get('league_id', False) and request.session['league_id'] == int(league_id):
        """
        https://docs.djangoproject.com/en/dev/topics/forms/formsets/
        https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#inline-formsets
        https://docs.djangoproject.com/en/dev/ref/forms/models/#django.forms.models.modelformset_factory
        """
        ContestantsFormSet = inlineformset_factory(Description, Contestants, form=ContestantsForm, formset=Required2FormSet, extra=0, can_delete=False)
        if request.method == 'POST':
            contestants_formset = ContestantsFormSet(request.POST, instance=league)
            if contestants_formset.is_valid():
            
                for form in contestants_formset.forms:
                    if form.has_changed():
                        form.save()
                
                return HttpResponseRedirect(reverse('leagues:detail', args=(league.id,)))
        else:
            contestants_formset = ContestantsFormSet(instance=league)
        
        return render(request, 'leagues/edit_names.html', {'contestants_formset': contestants_formset})
    else:
        return HttpResponseRedirect(reverse('leagues:detail', args=(league.id,)))

def delete(request, league_id):
    league = get_object_or_404(Description, pk=league_id)
    
    if request.session.get('league_id', False) and request.session['league_id'] == int(league_id):
        if request.method == 'POST':
            results = Results.objects.filter(league=league_id)
            contestants = Contestants.objects.filter(league=league_id)
            
            results.delete()
            contestants.delete()
            
            league.delete()
            
            return HttpResponseRedirect(reverse('leagues:index'))
        else:
            return render(request, 'leagues/delete.html')
    else:
        return HttpResponseRedirect(reverse('leagues:detail', args=(league.id,)))

def latest(request):
    all_leagues = Description.objects.all().order_by('-id')
    paginator = Paginator(all_leagues, 20)
    
    page = request.GET.get('page')
    try:
        leagues = paginator.page(page)
    except PageNotAnInteger:
        leagues = paginator.page(1)
    except EmptyPage:
        leagues = paginator.page(paginator.num_pages)
    is_paged = paginator.num_pages > 1
    
    return render(request, 'leagues/latest.html', {'all_leagues': leagues, 'is_paginated' : is_paged})
