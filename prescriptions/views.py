from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Disease
from .forms import DiseaseForm
from django.views.decorators.http import require_POST

from django.http import HttpResponse
from .models import ChatMessage,ChatResponseSuggestion,SymptomMedicine
from .forms import ChatMessageForm,ChatResponseSuggestionForm,SymptomMedicineForm
from django.forms import modelformset_factory
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from io import BytesIO
import datetime
import json
from django.http import JsonResponse
from django.urls import reverse





# Protect the select_disease view with login_required
@login_required
def home(request):
    diseases = Disease.objects.all()  # Fetch all diseases
    if request.method == 'POST':
        disease_id = request.POST.get('disease')
        if disease_id:
            return redirect('start_chat', disease_id=disease_id)

    return render(request, 'prescriptions/home.html', {'diseases': diseases})


# Disease List View
@login_required
def disease_list(request):
    diseases = Disease.objects.all()
    return render(request, 'prescriptions/disease_list.html', {'diseases': diseases})

# Disease Create View
@login_required
def disease_create(request):
    if request.method == 'POST':
        form = DiseaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('disease_list')
    else:
        form = DiseaseForm()
    return render(request, 'prescriptions/disease_form.html', {'form': form, 'title': 'Add Disease'})

# Disease Update View
@login_required
def disease_update(request, pk):
    disease = get_object_or_404(Disease, pk=pk)
    if request.method == 'POST':
        form = DiseaseForm(request.POST, instance=disease)
        if form.is_valid():
            form.save()
            return redirect('disease_list')
    else:
        form = DiseaseForm(instance=disease)
    return render(request, 'prescriptions/disease_form.html', {'form': form, 'title': 'Edit Disease'})


# Disease Delete View
@require_POST
@login_required
def disease_delete(request, pk):
    disease = get_object_or_404(Disease, pk=pk)
    disease.delete()
    return redirect('disease_list')





@login_required
def disease_chat(request, disease_id, chat_id=None):
    disease = get_object_or_404(Disease, id=disease_id)
    chat_messages = ChatMessage.objects.filter(disease=disease).order_by('-timestamp')

    if chat_id:
        chat_instance = get_object_or_404(ChatMessage, id=chat_id)
    else:
        chat_instance = None

    if request.method == 'POST':
        form = ChatMessageForm(request.POST, instance=chat_instance)
        if form.is_valid():
            chat = form.save(commit=False)
            chat.user = request.user
            chat.disease = disease
            chat.save()
            return redirect('disease_chat', disease_id=disease_id)
    else:
        form = ChatMessageForm(instance=chat_instance)

    return render(request, 'prescriptions/disease_chat.html', {
        'disease': disease,
        'form': form,
        'chat_messages': chat_messages,
        'chat_id': chat_id,
    })
    

@login_required
def chat_delete(request, chat_id):
    chat = get_object_or_404(ChatMessage, id=chat_id)
    disease_id = chat.disease.id
    if request.method == 'POST':
        chat.delete()
    return redirect('disease_chat', disease_id=disease_id)


def manage_possible_answers(request, message_id):
    chat_message = get_object_or_404(ChatMessage, id=message_id)
    suggestions = chat_message.suggestions.all()

    edit_suggestion = None
    if 'edit' in request.GET:
        edit_id = request.GET.get('edit')
        edit_suggestion = get_object_or_404(ChatResponseSuggestion, id=edit_id, chat_message=chat_message)

    if request.method == 'POST':
        form = ChatResponseSuggestionForm(request.POST, instance=edit_suggestion)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.chat_message = chat_message
            suggestion.save()
            return redirect('manage_possible_answers', message_id=message_id)
    else:
        form = ChatResponseSuggestionForm(instance=edit_suggestion)

    return render(request, 'prescriptions/manage_possible_answers.html', {
        'chat_message': chat_message,
        'form': form,
        'suggestions': suggestions,
        'edit_suggestion': edit_suggestion,
    })

    
    

def delete_possible_answer(request, suggestion_id):
    suggestion = get_object_or_404(ChatResponseSuggestion, id=suggestion_id)
    message_id = suggestion.chat_message.id
    suggestion.delete()
    return redirect('manage_possible_answers', message_id=message_id)




def manage_symptom_medicines(request, disease_id):
    disease = get_object_or_404(Disease, pk=disease_id)

    SymptomMedicineFormSet = modelformset_factory(
        SymptomMedicine,
        form=SymptomMedicineForm,
        extra=1,
        can_delete=True  # ✅ Allow deletions
    )

    queryset = SymptomMedicine.objects.filter(disease=disease)

    if request.method == 'POST':
        formset = SymptomMedicineFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            edited = False

            # Save new/updated instances
            instances = formset.save(commit=False)
            for instance in instances:
                instance.disease = disease
                instance.save()
                edited = True
            formset.save_m2m()

            # Redirect with appropriate message
            query_param = "edited=1" if edited else "saved=1"
            return redirect(f"{reverse('manage_symptom_medicines', args=[disease.id])}?{query_param}")
    else:
        formset = SymptomMedicineFormSet(queryset=queryset)

    return render(request, 'symptom_medicine/manage.html', {
        'formset': formset,
        'disease': disease
    })
    


@csrf_exempt
def delete_symptom_medicine(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            sm_id = data.get("id")
            obj = get_object_or_404(SymptomMedicine, pk=sm_id)
            obj.delete()
            return JsonResponse({"success": True, "message": "Deleted successfully."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request method."})







@login_required
def start_chat(request, disease_id):
    try:
        disease = Disease.objects.get(id=disease_id)
    except Disease.DoesNotExist:
        return redirect('home')

    request.session['chat_step'] = 0
    request.session['chat_complete'] = False
    return redirect('chat', disease_id=disease.id)





universal_chat_steps = [
    "Hi, do you feel weak?",
     "How long have you been feeling these symptoms?"
]

disease_specific_chat_steps = {
    "fever": ["How high is your fever?", "Do you feel chills?"],
    "cough": ["Is it dry or wet?", "Do you feel chest tightness?"],
    "cold": ["Runny nose?", "Sneezing often?"],
    "flu": ["Do you have fatigue?", "Muscle aches?"],
    "diabetes": ["Do you urinate often?", "Feeling very thirsty?"],
    "asthma": ["Do you wheeze when breathing?", "Shortness of breath?"],
    "hypertension": ["Do you have headaches?", "Any vision problems?"],
    "migraine": ["Light sensitivity?", "Nausea or vomiting?"],
    "allergy": ["Rashes or itching?", "Swelling in face or throat?"],
    "covid": ["Loss of taste or smell?", "Recent exposure to someone positive?"]
}

disease_specific_medicines = {
    "fever": ["Paracetamol", "Ibuprofen"],
    "cough": ["Cough Syrup", "Steam inhalation"],
    "cold": ["Antihistamines", "Vitamin C"],
    "flu": ["Oseltamivir", "Rest and fluids"],
    "diabetes": ["Metformin", "Glipizide"],
    "asthma": ["Inhaler", "Montelukast"],
    "hypertension": ["Amlodipine", "Lisinopril"],
    "migraine": ["Sumatriptan", "Ibuprofen"],
    "allergy": ["Cetirizine", "Loratadine"],
    "covid": ["Paracetamol", "Isolation and fluids"]
}

@login_required
def disease_list(request):
    diseases = Disease.objects.all()[:10]  # Show only 10
    return render(request, "prescriptions/disease_list.html", {"diseases": diseases})


@login_required
@csrf_exempt
def chat(request, disease_id):
    disease = get_object_or_404(Disease, id=disease_id)
    disease_key = disease.name.lower().strip().replace(" ", "_")

    if request.method == "GET":
        request.session['chat_step'] = 0
        request.session['chat_complete'] = False
        ChatMessage.objects.filter(user=request.user, disease=disease).delete()
        first_bot_msg = universal_chat_steps[0]
        ChatMessage.objects.create(user=request.user, disease=disease, message=first_bot_msg, is_bot=True)

    step = request.session.get('chat_step', 0)
    complete = request.session.get('chat_complete', False)

    if request.method == "POST" and not complete:
        user_input = request.POST.get("message")
        if user_input:
            ChatMessage.objects.create(user=request.user, message=user_input, is_bot=False, disease=disease)

        step += 1
        request.session['chat_step'] = step

        if step < len(universal_chat_steps):
            bot_msg = universal_chat_steps[step]
            ChatMessage.objects.create(user=request.user, message=bot_msg, is_bot=True, disease=disease)
        else:
            disease_questions = disease_specific_chat_steps.get(disease_key, [])
            disease_step = step - len(universal_chat_steps)

            if disease_step < len(disease_questions):
                bot_msg = disease_questions[disease_step]
                ChatMessage.objects.create(user=request.user, message=bot_msg, is_bot=True, disease=disease)
            else:
                ChatMessage.objects.create(user=request.user, message="Thank you. Here is your prescription:", is_bot=True, disease=disease)
                medicines = disease_specific_medicines.get(disease_key, ["Consult a doctor."])
                ChatMessage.objects.create(user=request.user, message="\n".join(medicines), is_bot=True, disease=disease)
                request.session['chat_complete'] = True

    messages = ChatMessage.objects.filter(user=request.user, disease=disease).order_by("timestamp")
    show_yes_no = not complete and step < len(universal_chat_steps)

    return render(request, "prescriptions/chatbot.html", {
        "messages": messages,
        "disease": disease,
        "show_yes_no": show_yes_no
    })




# View to handle PDF download for prescription
def download_prescription(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Fonts
    p.setFont("Helvetica-Bold", 16)
    p.drawString(30 * mm, height - 30 * mm, "Sunrise Medical Clinic")
    p.setFont("Helvetica", 11)
    p.drawString(30 * mm, height - 37 * mm, "Dr. Sarah Thompson, MBBS, MD")
    p.drawString(30 * mm, height - 44 * mm, "Contact: +880123456789 | Email: sunriseclinic@example.com")

    # Horizontal line
    p.line(25 * mm, height - 50 * mm, width - 25 * mm, height - 50 * mm)

    # Patient Info and Date
    p.setFont("Helvetica", 10)
    today = datetime.datetime.today().strftime('%d-%m-%Y')
    p.drawString(30 * mm, height - 60 * mm, f"Patient: ____________")
    p.drawString(120 * mm, height - 60 * mm, f"Date: {today}")

    # Prescription Title
    p.setFont("Helvetica-Bold", 12)
    p.drawString(30 * mm, height - 75 * mm, "Prescription")

    # Medicines
    p.setFont("Helvetica", 11)
    y = height - 90 * mm
    p.drawString(35 * mm, y, "• Paracetamol 500mg – 1 tablet three times daily after meals")
    y -= 12
    p.drawString(35 * mm, y, "• Cough Syrup – 5ml every 6 hours")
    y -= 12
    p.drawString(35 * mm, y, "• Rest and drink plenty of fluids")
    y -= 20
    p.drawString(35 * mm, y, "Note: Please follow the instructions and consult if symptoms persist.")

    # Signature
    p.drawString(130 * mm, 30 * mm, "____________________")
    p.drawString(145 * mm, 25 * mm, "Doctor's Signature")

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf', headers={
        'Content-Disposition': 'attachment; filename="prescription.pdf"',
    })