""" 
* ©Copyrights, all rights reserved at the exception of the used libraries.
* @author: Phileas Hocquard 
* The View file is responsible for handling Web Requests
* Location : /mainsite/popclick/views.py
"""

# division operation
from __future__ import division
# Request handling
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.http import StreamingHttpResponse
import requests
import json
# Time related expression
from datetime import datetime
from django.utils import timezone
import time
# data handling
from django.db import transaction, IntegrityError
from django.db.models import Q
# Import user model
from django.contrib.auth.models import User
# Authentication for admin users
from django.contrib.auth import authenticate
# Import model classes
from .models import Interest, PageobjectInterest, Visit, Website, SecureAuth
from .models import Page, Profile, ProfileInterest, PageObject, ProfilePageobject, PageobjectLog 
from .models import PageN, WebsiteN, ProfileN
# Neomodels field, relations and object representation
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
        RelationshipTo, RelationshipFrom)
# Neomodel configurations
from neomodel import db as neodb
from neomodel import config as neoconfig
# Operations
from django.core import serializers
from django.db.models import Max, Min
import random as rand
# Third party used libraries / Operations
import numpy as np
from numpy import *
from operator import itemgetter
from sklearn.preprocessing import normalize
from sklearn import preprocessing
from iteration_utilities import unique_everseen
# External Methods and classes
from popclick.populating import *
from popclick.interest_learning import *
from popclick.UU_based_filtering import *
# from popclick.tests import *
# Allows async task
import threading
# For testing

# index page of the application
def index(request):
    """ A simple HTTP request to verify that a connection is available with the server
    Return (HttpRespons(string))
    """
    return HttpResponse("Online Check.")


# Profile and User-User Demographic Based Collaborative filtering
@csrf_exempt
def get_suggestion(request, token):
    """ Get suggestions for a given token
    
    Args:
        token (string): Profile Token
    Received Data:
        JSON File: {auth, Array of clickable page items(text, href, page)}

    Returns:
        Render response with the ranked list of the received clickables index
    """
    if request.method == 'POST':
        # Loading Received information to a json format
        received_json_data = json.loads(request.body.decode('utf-8'))
        object_auth = received_json_data['profile']
        #  Getting profile information
        try:
            own_profile = Profile.objects.get(token=token)
            own_key = SecureAuth.objects.get(profile=own_profile).key
        except:
            return HttpResponseNotFound('Invalid Profile') 

        # Making sure the profile is activated and in order
        if own_profile and own_profile.activated and own_key == str(object_auth):
            try:
                # Remove all the pageobjects who do not have a relation with a profile.
                # PageObjectIntere
                # if Pa
                # Get last visit of user
                # Get last selected element of user location href href
                pageobjects = received_json_data['pageobjects']

                # Getting web page origin
                base_uri = pageobjects[0][0]
                handle_visit(own_profile, base_uri)
                handle_browsing_mistake(own_profile, base_uri)

                # Extracting the received pageobjects
                received_pageobjects_hrefs = [o[1] for o in pageobjects]
                received_pageobjects_text = [o[2] for o in pageobjects]
                received_pageobjects_selectors = [o[3] for o in pageobjects]
            # Throw an Index Error if there is a missmatch.
            except IndexError:
                context = {'base': "Current", 'recommendation': "None"}
                return render(request, 'suggestions.json', context)

            try:
                # Cross reference objects visible to the user and the stored objects
                page = Page.objects.get(href=base_uri)
                pageobjects = PageObject.objects.filter(page=page)
                match_pageobjects = set(pageobjects)
                matching_pageobjects_set = set(pageobjects.filter(text__in=received_pageobjects_text).values_list('id', flat=True))
                matching_pageobjects_set.update(pageobjects.filter(href__in=received_pageobjects_hrefs).values_list('id', flat=True))
                matching_pageobjects = pageobjects.filter(pk__in=matching_pageobjects_set)
                profiles_pageobjects = ProfilePageobject.objects.filter(pageobject__in=matching_pageobjects)
                profiles = Profile.objects.filter(id__in=profiles_pageobjects.values('profile').distinct())
                profiles_interests = ProfileInterest.objects.filter(profile__in=profiles)
                selectable_values = []
                pageobjectIndex_tokens = {}
                # Normalized profile pageobject selections among the profiles themselves.
                # Dictionaries for the profile page selections, profile ages, Standardized profile interests, standardized genders
                nm_pg_select = {}
                nm_pr_ages = {}
                std_pr_int = {}
                std_gender = {}
                # Find the oldest and youngest individuals
                lowest_age = profiles.aggregate(Min('age'))['age__min']
                highest_age = profiles.aggregate(Max('age'))['age__max']
                # List of all the interests
                interests = [i.name for i in Interest.objects.all().order_by('name')]
                # If their are no records of ages
                if highest_age is None or lowest_age is None:
                    context = {'base': base_uri, 'recommendation': "No known objects"}
                    return render(request, 'suggestions.json', context)
                # If the database only hase one user we have to handle a small age difference.
                if highest_age - lowest_age == 0:
                    lowest_age = lowest_age - 1
                # The different types of genders
                genders = ['Female', 'Male', 'Other', 'Irrelevant']

                # Standardising profile based attributes : Gender, Interests | Normalising profile based attributes : Age, Selections
                for profile in profiles :
                    # Retrieving highest and lowest number of selections.
                    lowest_nb_selections = profiles_pageobjects.filter(profile=profile).aggregate(Min('selections'))['selections__min']
                    highest_nb_selections = profiles_pageobjects.filter(profile=profile).aggregate(Max('selections'))['selections__max']
                    if int(highest_nb_selections) - int(lowest_nb_selections) == 0:
                        highest_nb_selections = highest_nb_selections + 1

                    # Normalising selectable value per pageobject
                    for pr_po in profiles_pageobjects.filter(profile=profile):
                        nm_pg_select[str(pr_po.id)] = float(pr_po.selections-int(lowest_nb_selections))/float(
                                int(highest_nb_selections)-int(lowest_nb_selections))

                    nm_pr_ages[str(profile.id)] = float((profile.age-lowest_age)/(highest_age-lowest_age))
                    
                    # Standardized the profile's gender
                    standardized_profile_gender = [0]*(len(genders))
                    # Standardising gender creating two rows containing 0's and 1's
                    standardized_profile_gender[genders.index(profile.gender)] = 1

                    # Add standardised list of profile interests to the dictionary of standardised interests
                    std_pr_int[str(profile.id)] = get_formatted_user_or_pageobject_interests(profile)
                    # Add standardised list of profile gender to the dictionary of standardised gender 
                    std_gender[str(profile.id)] = [standardized_profile_gender]

                # Ordered list of pageobjects
                po_indexs = []
                # Dictionary of normalised Age per profile per page object
                po_norm_age = {}
                #  Dictionary of normalised Selections per profile per page objects
                po_norm_select = {}
                # For each object obtain add each user profile interests or gender value
                # (The matrix will be normalized)
                po_std_norm_interests_matrix = []
                po_std_norm_gender_matrix = []
                for po in matching_pageobjects.order_by('href'):
                    # Adding page object to the list to allow indexing
                    po_indexs.append(po)
                    # Number of profiles who used the page object
                    po_l = int(profiles_pageobjects.filter(pageobject=po).distinct().count())
                    # Default values
                    pr_po_mn_select = 0
                    pr_po_mn_age = 0
                    pr_po_std_mn_interests = []
                    pr_po_std_mn_gender = []
                    # For each profile mapped to an object
                    for pr_po in profiles_pageobjects.filter(pageobject=po):
                        current_element_index = -1
                        if po.text in received_pageobjects_text:
                            current_element_index = received_pageobjects_text.index(po.text)
                        else:
                            current_element_index = received_pageobjects_hrefs.index(po.href)
                        pageobjectIndex_tokens.setdefault(current_element_index, []).append(pr_po.profile.token)
                        # Add the profile normalised selections and age of the object/Profile
                        pr_po_mn_select += float(nm_pg_select[str(pr_po.id)])
                        pr_po_mn_age += float(nm_pr_ages[str(pr_po.profile.id)])
                        # Add to the array interest/gender array or initialise it
                        if len(pr_po_std_mn_interests) == 0:
                            pr_po_std_mn_interests = std_pr_int[str(pr_po.profile.id)]
                        else:
                            pr_po_std_mn_interests = np.add(pr_po_std_mn_interests, std_pr_int[str(pr_po.profile.id)])
                        if len(pr_po_std_mn_gender) == 0:
                            pr_po_std_mn_gender = std_gender[str(pr_po.profile.id)]
                        else:
                            pr_po_std_mn_gender = np.add(pr_po_std_mn_gender, std_gender[str(pr_po.profile.id)])
                    # Page object standardised to be normalised interest/gender matrix
                    po_std_norm_interests_matrix[len(po_std_norm_interests_matrix):] = [pr_po_std_mn_interests]
                    po_std_norm_gender_matrix[len(po_std_norm_gender_matrix):] = pr_po_std_mn_gender
                    # Normalise the selection and age prior
                    pr_po_mn_select /= po_l
                    po_norm_select[po] = [pr_po_mn_select]
                    pr_po_mn_age /= po_l
                    po_norm_age[po] = [pr_po_mn_age]

                complete_matrix = []
                # Converting to numpy array and normalise interest sub-matrix to allow PageobjecIntests to exist
                postdnormintmtx = np.array(po_std_norm_interests_matrix)
                postdnormintmtx = normalize(postdnormintmtx, axis=0, norm='l1')

                # It is necessary to hold a current reference to the pageobject interests for the learning process
                thr = threading.Thread(target=pageobject_interests_update(interests, po_indexs, postdnormintmtx), args=(), kwargs={})
                thr.start()

                postdnormgendmtx = np.array(po_std_norm_gender_matrix)
                np.seterr(divide='ignore', invalid='ignore')

                # Create the complete matrix
                # Matrix structure : age, interests , gender, selection
                for po in matching_pageobjects.order_by('href'):
                    complete_matrix.append(np.append(np.append(np.append(np.append(po_norm_age[po],
                        postdnormintmtx[po_indexs.index(po)]),
                    postdnormgendmtx[po_indexs.index(po)]),
                    po_norm_select[po]),
                    (1.0-float(time.mktime(po.updated_at.now().timetuple()))/float(time.mktime(datetime.now().timetuple())))))
                
                # Individual Row, Could be simplified to simply getting the actual user row in the matrix
                standardized_own_profile_gender = [0]*(len(genders))
                standardized_own_profile_gender[genders.index(own_profile.gender)] = 1

                standardized_own_profile_interests = get_formatted_user_or_pageobject_interests(own_profile)
                own_porfile_properties = np.append([float((profile.age-lowest_age)/(highest_age-lowest_age))],
                    np.append(standardized_own_profile_interests,
                    np.append(standardized_own_profile_gender, 
                    np.append([1.0],[1.0]))))

                # Normalize columns
                complete_matrix = np.matrix(normalize(complete_matrix, axis=0, norm='l1'))

                #  Computing the Euclidean Distance between 
                #  the Complete Matrix items and given Profile for KNN.
                profile_po_distance = []
                for rows in range(complete_matrix.shape[0]):
                    current_row = 0
                    for columns in range(complete_matrix.shape[1]):
                        current_row += np.square(own_porfile_properties[columns]-complete_matrix.item(rows,columns))
                    profile_po_distance.append((po_indexs[rows],(np.sqrt(current_row))))

                # Transform the dictionary to a sorted list of items mapped 
                # to the originally received clickable indexs
                itemIndex_distance = {}
                for item in profile_po_distance:
                    if item[0].text in received_pageobjects_text:
                        itemIndex_distance[received_pageobjects_text.index(item[0].text)] = item[1]
                    else:
                        itemIndex_distance[received_pageobjects_hrefs.index(item[0].href)] = item[1]
                error_flag = ""

                # ProfileBased and UU Demographic filtering
                User_Item_and_User_User_demographic = UI_UU_mixed_filtering(base_uri, token, pageobjectIndex_tokens, itemIndex_distance)
                # Sorted index list
                final_received_clickables_ranked_indexs = User_Item_and_User_User_demographic[0]
                # error_flag if any, depending on if neo4j is available
                error_flag = User_Item_and_User_User_demographic[1]
                # Ranks
                ranks = User_Item_and_User_User_demographic[2]
                # To be sent content with recommendation
                context = {'base':ranks, 'recommendation': final_received_clickables_ranked_indexs, 'error': error_flag}
            # Exception thrown if no page is available
            except (Page.DoesNotExist):
                # To be sent content with warning
                context = {'base': base_uri, 'recommendation': "No known objects"}
            # Key violation caused by the user
            except KeyError as e:
                # To be sent content with warning
                context = {'base': base_uri, 'recommendation': "Cross matching issue"}
            #  Render the created content in the form of a json file
            return render(request, 'suggestions.json', context)
        else:
            # If the user is not authenticated throw an error
            context = {'base': "Token Issue", 'recommendation': "Authentication Token or Key do not match"}
            return render(request, 'suggestions.json', context)

@csrf_exempt
def populate_selectable(request, token):
    """ populates the given selectable as well as classes involved for the creation of the pageobject relation
    
    Args:
        token (string): Profile Token
    Received Data:
        JSON Object: {local operation, page, profile, object_pageobject}

    Returns:
        Render response giving a confirmation that some action has taken place
    """
    if request.method == 'POST':
        received_json_data = json.loads(request.body.decode('utf-8'))
        # Decompose the JSON object
        object_profile = received_json_data['profile']
        object_pageobject = received_json_data['pageobject']
        object_interaction = received_json_data['interaction']
        object_auth = object_profile[0]
        object_logtime = datetime.strptime(object_profile[1], r'%Y-%m-%d %H:%M')
        try:
            profile = Profile.objects.get(token=token)
        except (Profile.DoesNotExist):
            context = {'inter' : 'e_profile_DoesNotExist'}
            return render(request, 'selectable_addition.json', context)
        # If the profile exists, its key is valid, and the profile is activated
        if profile and profile.activated and SecureAuth.objects.get(profile=profile).key == str(object_auth):
            # Matching all json items from the object to an individual object
            object_website = object_pageobject[4]
            object_page_path = object_pageobject[5]
            object_page = object_pageobject[0]
            object_href = object_pageobject[1]
            object_text = object_pageobject[2]
            object_selector = object_pageobject[3]
            object_operation =  object_interaction[0]
            object_clicks = object_interaction[1]
            # We do not keep a recollection of activity done on the localhost.
            if "localhost:" not in object_page:
                # If there isn't an attempt of data corruption
                try:
                    # Update or create each of the matching items
                    handle_Website(object_website)
                    page = handle_Page(object_website, object_page_path, object_page)
                    pageobject = handle_PageObject(object_selector, object_href, object_page, object_text)
                    handle_visit(profile, page)
                    profile_pageobject = handle_Profile_PageObject(profile, pageobject)
                    handle_PageobjectLog(profile, pageobject)
                except IntegrityError:
                    context = {'inter' : 'e_data_corruption'}
                    return render(request, 'selectable_addition.json', context)

                # Starting a new thread to learn on profile interests having an updated/created pageobject
                learning_thread = threading.Thread(target=learn_interests(profile, pageobject), args=(), kwargs={})
                learning_thread.start()
                
                # If the neo server is disconnected
                try:
                    # Create new nodes for each object.
                    # Get or create is applied as neo_4j interruptions may happen.
                    with neodb.transaction:
                        websiten = WebsiteN.get_or_create({'host': ''+object_website})
                        pagen = PageN.get_or_create({'href': object_href})
                        websiten = WebsiteN.nodes.get(host=object_website)
                        pagen = PageN.nodes.get(href=object_href)
                        pagen.website.connect(websiten)
                        profilen = ProfileN.get_or_create({'token': ''+profile.token})
                        profilen = ProfileN.nodes.get(token=token)
                        profilen.page.connect(pagen)
                        profilen.website.connect(websiten)
                except:
                    context = {'inter' : 'e_neo4j_Disconnected'}
                    return render(request, 'selectable_addition.json', context)
                # Returning information concerning the action took
                # This is formally for the developer of the plateform
                # As it doens't reveal any sensitive information we may send this as a response
                context = { 'prof':object_profile, 'obj':pageobject, 'inter':object_interaction}
            else:
                # The item is from localhost
                context = { 'storing': 'Refusing_to_store'}
        else:
            # The account is not activated therefore we should not permit the creation of a pageobject
            # as the object would be associated with their profile.
            context = { 'error' : 'not_activated'}
        # Return a json file containing the defined context above
        return render(request, 'selectable_addition.json', context)

# ---- Profile Related section ----
@csrf_exempt
def keygen(request, key):
    """ Generates a new key for a given profile eventual making the previous unusable
    Args:
        key (string): Profile Token
    Returns:
        HttpResponse(string)
    """
    # Get the token & key
    own_profile = Profile.objects.get(token=key)
    own_key = SecureAuth(profile=own_profile, key=own_profile.auth)
    # Save new key
    own_key.save()
    # Return CONFIRMATION
    return HttpResponse("New Key generated")

@csrf_exempt
def valid_profile(request, token):
    """ Get suggestions for a given token
    
    Args:
        token (string): Profile Token
    Received Data:
        JSON File: {auth}

    Returns:
        HttpResponse(String)
    """
    try:
        # Get specific profile
        own_profile = Profile.objects.get(token=token)
        own_auth = SecureAuth.objects.get(profile=own_profile)
        received_json_data = json.loads(request.body.decode('utf-8'))
        object_auth = received_json_data['profile']
    #  If there is in fact no known profile
    except (Profile.DoesNotExist):
        return HttpResponse("Invalid")
    # The profile is active therefore validate response
    if own_profile and own_auth and own_auth.key == str(object_auth):
        return HttpResponse("Valid")
    else:
        # The profile is either not active, authenticated.
        return HttpResponse("Invalid")

@csrf_exempt
# Send profile secure auth
def get_initial_auth(request, token):
    """ Requesting an authentication code for a specific token
    
    Args:
        token (string): Profile Token

    Returns:
        JSON File: {auth} auth.json
    """
    if request.method == 'GET':
        profile = Profile.objects.get(token=token)
        secure_auth = SecureAuth.objects.get(profile=profile).key
        # Make the profile active
        if profile.activated == False:
            profile.activated = True
            profile.save()
            # Create Profile Node
            try:
                with neodb.transaction:
                    profilen = ProfileN.get_or_create({'token': ''+profile.token})
            except:
                ""
            context = { 'auth' : secure_auth }
        else:
            context = { 'auth' : '' }
        # Reutrn an auth if it wasn't previously given
        return render(request, 'auth.json', context)

@csrf_exempt
# As the name suggests, it creates a profile
def create_profile(request):
    """ Verifies that a profile is valie
    
    Received Data:
        (JSON object): json_object
    Returns:
        Render create_profile.json{new_profile| profile_error}
    """
    Interests = ['News & Media','Fashion','Tech',
    'Finance & Economics','Music','Cars','Sports','Games & Tech','Shopping','Literature',
    'Travel','Arts','Social Awareness','Science','Movies & Theatre','Craft']
    if request.method == 'POST':
        # JSON decode error handling
        received_json_data= json.loads(request.body.decode('utf-8'))
        if profile_create_check(received_json_data, Interests) == "VALIDATED":
            #Have to add a response if one of age, token, auth, gender, logtime is wrong
            private_k = randToken()
            # Create a profile.
            new_profile = Profile(
                    age=int(datetime.today().year)-int(received_json_data['age']), 
                    token=randToken(),
                    gender=received_json_data['gender'],
                    logtime=datetime.strptime(received_json_data['logtime'], r'%Y-%m-%d %H:%M'))
            new_profile.save()
            # Create an encrypted authentication key
            new_secureauth = SecureAuth(profile=new_profile, key=private_k)
            new_secureauth.save()
            # Create three profile_interest objects.
            for interest in received_json_data['interests']:
                if interest in Interests:
                    new_interest = Interest(name=interest)
                    new_interest.save()
                    new_profile_interest = ProfileInterest(profile=new_profile, interest=new_interest)
                    new_profile_interest.save()
            context = { 'profile' : new_profile }
        else:
            context = { 'profile_error' : profile_create_check(received_json_data, Interests) }
        return render(request, 'create_profile.json', context)

# A profile must have a valid age, gender, logtime and at least 3 interests.
def profile_create_check(json_object, Interests):
    """ Verifies that a profile is valid
    
    Args:
        (JSON OBJECT): json_object contains user submitted profile
        (Interests): All the existing interest's names
    Returns:
        ERROR code or number of interests selected
    """
    # The json attributes must be the following
    if {"age", "gender", "logtime", "interests", "signed"} <= json_object.keys():
        # The user must be at least 3 years old and valid.
        if not (RepresentsInt(json_object['age']) and int(json_object['age']) > 3 and int(json_object['age']) < 120):
            return "INVALID_AGE"
        else:
            # The choosen gender of the individual must fall in following categories
            if not str(json_object['gender']) in ["Male","Female","Other","Irrelevant"]:
                return "INVALID_GENDER"
            else:
                try:
                    # The contract must be signed
                    if json_object['signed'] != 1:
                        return "NOT_SIGNED"
                    own_interests = 0
                    # The number of valid interests
                    for inter in json_object['interests']:
                        if inter in Interests:
                            own_interests+=1
                    # The user must have at least choosen 3 interests and no more than the number of known Interests
                    if not 3 <= own_interests < len(Interests):
                        return "WRONG_INTERESTS"
                    else:
                        # The profile contains all the necessary criterias
                        return "VALIDATED"
                except ValueError:
                    # Wrong time format
                    return "WRONG_DATE_FORMAT"
    else:
        # User fiddling
        return "MISSING_ATTRIBUTE"
        
# Only add element if it the page has been visited for more than 5 seconds without coming back to origin.
def handle_browsing_mistake(profile, base_uri):
    """ Verifying if a recent ProfilePageobject should be removed
    
    Args:
        profile (Profile): given profile
        base_uri (string): the visited web page of a potential pageobject
    """
    # Retreiving last ProfilePageobject relation
    try:
        last_object_visited_by_profile = ProfilePageobject.objects.filter(profile=profile).last() 
        if last_object_visited_by_profile != None and last_object_visited_by_profile.pageobject != None:
            # The visited uri of the last destination taken by a pageobject
            l_o_v_b_p_href = last_object_visited_by_profile.pageobject.href
            # The pageobject page source
            l_o_v_b_p_page_href = last_object_visited_by_profile.pageobject.page.href
            l_o_v_b_p_time = last_object_visited_by_profile.created_at
            if l_o_v_b_p_href != l_o_v_b_p_page_href and last_object_visited_by_profile.selections == 1:
                # If the user has created the pageobject in a short time period
                if base_uri == l_o_v_b_p_page_href and (timezone.now() - l_o_v_b_p_time).total_seconds() < 5.0:
                    # If the profile is the only one having the pageobject as a relation, then remove it
                    if len(ProfilePageobject.objects.filter(profile=profile,
                        pageobject=last_object_visited_by_profile.pageobject)) == 1:
                        last_object_visited_by_profile.pageobject.delete()
                    # Delete the Profilepageobject instance.
                    last_object_visited_by_profile.delete()
    except:
        # There is no existing block therefore we have no choice but to catch an exception
        "No object object to remove"

@csrf_exempt
def destroy_profile(request, profile, auth):
    """
    Destroy profile on command.
    Args:
        (profile): token
        (auth): SecureAuth.key
    """
    try:
        own_profile = Profile.objects.get(token=profile)
        own_key = SecureAuth.objects.get(profile=auth).key
        if own_profile and own_key:
            own_profile.delete()
            return HttpResponse("Ok")
    except:
        return HttpResponseNotFound('<h1>Invalid Credentials</h1>')

# If the element can be represented as an integer
def RepresentsInt(s):
    """ Integer representation
    
    Args:
        (object): s

    Returns:
        int(s)
    """
    try: 
        int(s)
        return True
    except ValueError:
        return False

def randToken():
    """ Random token generator
    Returns:
        (string)
    """
    a = '0123456789abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ'
    return "".join([rand.choice(a) for _ in range(20)])