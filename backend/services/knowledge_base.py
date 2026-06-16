# backend/services/knowledge_base.py
"""
BML College Knowledge Base
All college info, FAQs, and intent patterns.
Tiered: keyword match → TF-IDF → Ollama fallback.
"""

COLLEGE_KNOWLEDGE = {
    # ── GENERAL ──────────────────────────────────────────────────────────
    "welcome": {
        "response": (
            "👋 Welcome to BML College! I'm your AI assistant.\n\n"
            "I can help you with:\n"
            "• 📚 Courses & Programmes\n"
            "• 🌍 Study Abroad opportunities\n"
            "• 💰 Fees & Scholarships\n"
            "• 📝 Admissions & Applications\n"
            "• 🏫 Campus information\n"
            "• 🎓 Accreditations\n\n"
            "What would you like to know? 😊"
        ),
        "quick_replies": ["Courses", "Fees", "Admissions", "Study Abroad", "Contact Us"]
    },

    "about": {
        "keywords": ["about", "who are you", "what is bml", "tell me about", "history", "established", "founded"],
        "response": (
            "🏫 **About BML College**\n\n"
            "BML College UK & International was **established in 2012** in the heart of Birmingham.\n\n"
            "We believe quality education should be **affordable and accessible** to everyone worldwide.\n\n"
            "📍 **UK Campus:** Farm Street, Hockley, Birmingham, B19 2TZ\n"
            "📍 **Sri Lanka Campus:** 163/4, New Kandy Road, Malabe\n\n"
            "🏆 **Key Facts:**\n"
            "• 97% student success rate\n"
            "• 1,000+ students enrolled\n"
            "• 39+ programmes offered\n"
            "• Direct university entry routes in UK, USA, Canada, Australia & Europe"
        ),
        "quick_replies": ["Our Courses", "Accreditations", "Contact", "Apply Now"]
    },

    # ── COURSES ───────────────────────────────────────────────────────────
    "courses": {
        "keywords": ["course", "programme", "program", "study", "degree", "diploma", "certificate",
                     "undergraduate", "postgraduate", "masters", "mba", "bachelor", "foundation",
                     "what do you offer", "available courses"],
        "response": (
            "📚 **BML College Programmes**\n\n"
            "**🏢 Arts & Social Sciences**\n"
            "• Business School — Diploma to MBA level\n"
            "• School of Education\n"
            "• School of Languages\n"
            "• School of Law\n"
            "• School of Hospitality & Tourism\n\n"
            "**🏥 Health & Medical Sciences**\n"
            "• School of Psychology\n"
            "• School of Health Sciences\n\n"
            "**💻 Engineering & Technology**\n"
            "• School of Electrical, Electronic & Mechanical Engineering\n"
            "• School of Computer Science & Technology\n\n"
            "Levels offered: Level 3 (Foundation) → Level 4/5 (HNC/HND) → Level 6 (Degree) → Level 7 (Masters)"
        ),
        "quick_replies": ["Business Courses", "IT Courses", "Health Courses", "Course Fees", "Apply Now"]
    },

    "business": {
        "keywords": ["business", "mba", "management", "marketing", "finance", "accounting", "commerce"],
        "response": (
            "🏢 **Business School Programmes**\n\n"
            "• **Level 3** – Diploma in Business Management\n"
            "• **Level 4** – Higher National Certificate in Business\n"
            "• **Level 5** – Higher National Diploma in Business\n"
            "• **Level 6** – BA (Hons) Business Management\n"
            "• **Level 7** – MBA (Master of Business Administration)\n\n"
            "All programmes are **OTHM Accredited** and provide direct entry routes to UK universities.\n\n"
            "🎯 Specialisations: Marketing, Finance, Human Resources, International Business"
        ),
        "quick_replies": ["MBA Details", "Course Fees", "Entry Requirements", "Apply Now"]
    },

    "it_courses": {
        "keywords": ["computer", "it", "technology", "software", "programming", "information technology",
                     "cyber", "networking", "data science", "ai", "computing"],
        "response": (
            "💻 **Computer Science & Technology Programmes**\n\n"
            "• **Level 3** – Foundation Diploma in Information Technology\n"
            "• **Level 4** – HNC in Computing\n"
            "• **Level 5** – HND in Computing\n"
            "• **Level 6** – BSc (Hons) Computer Science\n\n"
            "Also offered by the Engineering School:\n"
            "• Electrical & Electronic Engineering\n"
            "• Mechanical Engineering\n\n"
            "📌 Accredited by OTHM | Microsoft Partner Institution"
        ),
        "quick_replies": ["Course Fees", "Entry Requirements", "Study Abroad in IT", "Apply"]
    },

    "health": {
        "keywords": ["health", "psychology", "nursing", "medical", "care", "social care", "counselling",
                     "mental health", "pharmacology", "physiotherapy"],
        "response": (
            "🏥 **Health & Medical Sciences Programmes**\n\n"
            "**School of Psychology:**\n"
            "• Level 4–7 Psychology programmes\n"
            "• Counselling & Psychotherapy\n"
            "• Mental Health Studies\n\n"
            "**School of Health Sciences:**\n"
            "• Health & Social Care (Levels 3–7)\n"
            "• Healthcare Management\n"
            "• Nursing pathway programmes\n\n"
            "📣 Recent news: 50% tuition scholarships available for January 2026 intake!\n\n"
            "BML is a **Skills for Care** approved centre."
        ),
        "quick_replies": ["Scholarships", "Course Fees", "Study Abroad", "Apply Now"]
    },

    # ── FEES ──────────────────────────────────────────────────────────────
    "fees": {
        "keywords": ["fee", "fees", "cost", "price", "tuition", "how much", "payment", "installment",
                     "afford", "expensive", "cheap", "scholarship", "discount", "bursary", "financial"],
        "response": (
            "💰 **Tuition Fees at BML College**\n\n"
            "Fees vary by programme level:\n\n"
            "• **Level 3 (Foundation)** – From £1,200 / LKR equivalent\n"
            "• **Level 4/5 (HNC/HND)** – From £2,500\n"
            "• **Level 6 (Degree)** – From £4,500\n"
            "• **Level 7 (Masters/MBA)** – From £5,500\n\n"
            "✨ **Current Offer:** 50% Scholarship for January 2026 intake!\n\n"
            "💳 Payment plans available — pay in instalments\n"
            "🌏 Different rates for Sri Lanka campus\n\n"
            "For exact fees, please contact admissions."
        ),
        "quick_replies": ["Apply for Scholarship", "Payment Plans", "Contact Admissions", "Apply Now"]
    },

    "scholarship": {
        "keywords": ["scholarship", "grant", "bursary", "financial aid", "discount", "free", "50%", "reduced"],
        "response": (
            "🎓 **Scholarships & Financial Aid**\n\n"
            "**Current Offer: 50% Tuition Scholarship**\n"
            "Available for students joining in the **January 2026 intake**!\n\n"
            "**How to apply:**\n"
            "1. Submit your application via cms.bmlcollege.com\n"
            "2. Mention the scholarship in your application\n"
            "3. Our admissions team will confirm eligibility\n\n"
            "📧 Email: info@bmlcollege.com\n"
            "📞 UK: +44 (0) 121 523 0141"
        ),
        "quick_replies": ["Apply Now", "Contact Admissions", "Fees Overview"]
    },

    # ── ADMISSIONS ────────────────────────────────────────────────────────
    "admissions": {
        "keywords": ["admission", "apply", "application", "enroll", "enrol", "register", "intake",
                     "how to join", "join", "start", "entry", "requirement", "eligibility", "qualify",
                     "when can i", "when does"],
        "response": (
            "📝 **Admissions at BML College**\n\n"
            "**Entry Requirements:**\n"
            "• Level 3: No prior qualifications needed (school leavers welcome)\n"
            "• Level 4/5: Level 3 certificate or equivalent\n"
            "• Level 6 (Degree): HND or equivalent\n"
            "• Level 7 (Masters): Bachelor's degree\n\n"
            "**Intakes:** January, April, September\n\n"
            "**How to Apply:**\n"
            "1. Visit 🔗 cms.bmlcollege.com\n"
            "2. Create a free account\n"
            "3. Select your programme\n"
            "4. Upload documents\n"
            "5. Pay registration fee\n\n"
            "📧 info@bmlcollege.com | ☎ +44 121 523 0141"
        ),
        "quick_replies": ["Apply Online", "Entry Requirements", "January Intake", "Contact Admissions"]
    },

    "documents": {
        "keywords": ["document", "passport", "certificate", "transcript", "ielts", "english", "language",
                     "visa", "id", "proof", "qualification", "upload"],
        "response": (
            "📋 **Required Documents for Admission**\n\n"
            "• Valid Passport or National ID\n"
            "• Previous academic certificates/transcripts\n"
            "• English language proof (if applicable):\n"
            "  – IELTS 5.5+ or equivalent, OR\n"
            "  – Prior education in English medium\n"
            "• Passport-size photograph\n"
            "• Personal statement (for degree/masters level)\n\n"
            "📌 All documents can be uploaded digitally via our student portal.\n\n"
            "Need help? Our admissions team is happy to assist!"
        ),
        "quick_replies": ["Apply Now", "Contact Admissions", "IELTS Requirements"]
    },

    # ── STUDY ABROAD ─────────────────────────────────────────────────────
    "study_abroad": {
        "keywords": ["study abroad", "abroad", "uk", "australia", "canada", "usa", "america", "europe",
                     "new zealand", "overseas", "international", "migration", "immigration", "visa",
                     "go to uk", "move to"],
        "response": (
            "🌍 **Study Abroad with BML College**\n\n"
            "BML graduates get **direct entry** to top universities worldwide!\n\n"
            "**Destinations:**\n"
            "🇬🇧 **United Kingdom** – Top UK universities\n"
            "🇦🇺 **Australia & New Zealand** – Including University of Sydney\n"
            "🇨🇦 **Canada & USA** – North American universities\n"
            "🇪🇺 **Europe** – EU university pathways\n\n"
            "**Our Partners include:**\n"
            "• Coventry University\n"
            "• University of Sussex\n"
            "• Taylor's College\n"
            "• University of Sydney\n\n"
            "Start your BML programme → complete abroad!"
        ),
        "quick_replies": ["UK Universities", "Australia", "Canada & USA", "Apply Now"]
    },

    # ── CAMPUS ────────────────────────────────────────────────────────────
    "campus": {
        "keywords": ["campus", "location", "address", "where", "birmingham", "malabe", "sri lanka",
                     "hockley", "farm street", "find you", "directions"],
        "response": (
            "📍 **Our Campuses**\n\n"
            "**🇬🇧 UK Campus (Main)**\n"
            "Farm Street, Hockley, Birmingham, B19 2TZ\n"
            "📞 +44 (0) 121 523 0141\n"
            "Central Birmingham location — excellent transport links\n\n"
            "**🇱🇰 Sri Lanka Campus**\n"
            "163/4, New Kandy Road, Malabe, 10115\n"
            "📞 +94 (0) 112 19 6789\n\n"
            "**Online Learning:**\n"
            "Many programmes also available 100% online.\n"
            "Login to LMS: bmlcollege.com/connect"
        ),
        "quick_replies": ["Get Directions", "Online Learning", "Contact Us"]
    },

    # ── ACCREDITATIONS ────────────────────────────────────────────────────
    "accreditation": {
        "keywords": ["accredit", "recognised", "recognized", "valid", "legit", "approved", "othm",
                     "ukrlp", "ofqual", "quality", "regulated", "registered", "ico", "microsoft"],
        "response": (
            "🏆 **Accreditations & Approvals**\n\n"
            "BML College is fully recognised and accredited:\n\n"
            "• 🏅 **OTHM Awarding Body** – Approved Centre No: DC1811288\n"
            "• 🇬🇧 **UKRLP Registered** – PRN: 10057499\n"
            "• 🏛️ **UK Registered Company** – No: 15825578\n"
            "• 🔒 **ICO Registered** (Data Protection)\n"
            "• 💻 **Microsoft Partner** Institution\n"
            "• 🏥 **Skills for Care** Approved Centre\n"
            "• 📚 **British Council** Recognised\n"
            "• 🤝 **ApplyBoard** Partner\n\n"
            "Our qualifications are internationally recognised!"
        ),
        "quick_replies": ["About OTHM", "Study Abroad", "Course Info"]
    },

    # ── CONTACT ───────────────────────────────────────────────────────────
    "contact": {
        "keywords": ["contact", "phone", "email", "call", "reach", "get in touch", "speak", "talk",
                     "number", "address", "whatsapp", "message", "social media"],
        "response": (
            "📞 **Contact BML College**\n\n"
            "**🇬🇧 UK Office:**\n"
            "📞 +44 (0) 121 523 0141\n"
            "📍 Farm Street, Hockley, Birmingham, B19 2TZ\n\n"
            "**🇱🇰 Sri Lanka Office:**\n"
            "📞 +94 (0) 112 19 6789\n"
            "📍 163/4, New Kandy Road, Malabe\n\n"
            "📧 info@bmlcollege.com\n\n"
            "**Social Media:**\n"
            "📘 Facebook: /BMLCollegeUK\n"
            "📸 Instagram: @bmlcollegeuk\n\n"
            "⏰ Working Hours: Mon–Fri, 9:00 AM – 5:00 PM (UK time)"
        ),
        "quick_replies": ["Talk to Agent", "Apply Now", "Visit Campus"]
    },

    # ── LMS / PORTAL ─────────────────────────────────────────────────────
    "lms": {
        "keywords": ["lms", "portal", "login", "online", "student portal", "e-learning", "elearning",
                     "access", "moodle", "password", "account", "log in", "sign in"],
        "response": (
            "🖥️ **Student Learning Portal (LMS)**\n\n"
            "Access your courses, materials and grades online:\n\n"
            "🔗 **Login:** bmlcollege.com/connect\n\n"
            "**New Student? Register at:**\n"
            "🔗 cms.bmlcollege.com\n\n"
            "**Having trouble logging in?**\n"
            "📧 Email: info@bmlcollege.com\n"
            "📞 Call: +44 (0) 121 523 0141\n\n"
            "Our tech team will help you get access within 24 hours."
        ),
        "quick_replies": ["Go to LMS", "Registration Help", "Contact Support"]
    },

    # ── HUMAN AGENT ──────────────────────────────────────────────────────
    "human_agent": {
        "keywords": ["human", "agent", "person", "staff", "advisor", "counsellor", "counselor",
                     "speak to someone", "talk to someone", "real person", "not robot", "help me more",
                     "more help", "support", "live chat", "transfer", "connect me"],
        "response": (
            "👤 **Connecting you to a Human Agent**\n\n"
            "You'll be transferred to our support team shortly.\n\n"
            "⏰ Working Hours: Mon–Fri, 9:00 AM – 5:00 PM (UK time)\n\n"
            "If it's outside working hours, we'll get back to you as soon as possible.\n\n"
            "Alternatively:\n"
            "📧 info@bmlcollege.com\n"
            "📞 +44 (0) 121 523 0141"
        ),
        "quick_replies": []
    },

    # ── ALUMNI ────────────────────────────────────────────────────────────
    "alumni": {
        "keywords": ["alumni", "graduate", "former student", "past student", "alumni network"],
        "response": (
            "🎓 **BML Alumni Network**\n\n"
            "Join our growing community of BML graduates worldwide!\n\n"
            "Our alumni are successfully working and studying in:\n"
            "🇬🇧 UK | 🇦🇺 Australia | 🇨🇦 Canada | 🇺🇸 USA | 🇪🇺 Europe and beyond.\n\n"
            "**Register as Alumni:**\n"
            "🔗 bmlcollege.com/alumni\n\n"
            "Stay connected with your college community!"
        ),
        "quick_replies": ["Alumni Page", "Study Abroad", "Contact Us"]
    },

    # ── BML JUNIOR ────────────────────────────────────────────────────────
    "junior": {
        "keywords": ["junior", "montessori", "daycare", "day care", "nursery", "child", "kids",
                     "preschool", "pre-school", "kindergarten"],
        "response": (
            "👶 **BML Junior – Montessori & Day Care**\n\n"
            "BML Junior is our early childhood education centre located in **Sri Lanka**.\n\n"
            "Offering:\n"
            "• Montessori education\n"
            "• Day care services\n"
            "• Child-centred learning approach\n\n"
            "📞 Contact Sri Lanka campus: +94 (0) 112 19 6789\n"
            "📧 info@bmlcollege.com"
        ),
        "quick_replies": ["Sri Lanka Campus", "Contact Us", "Other Programmes"]
    },

    # ── GREETINGS ─────────────────────────────────────────────────────────
    "greeting": {
        "keywords": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening",
                     "howdy", "greetings", "what's up", "sup"],
        "response": (
            "Hello! 👋 Welcome to BML College!\n\n"
            "I'm here to help you with information about our programmes, admissions, fees, and more.\n\n"
            "What can I help you with today?"
        ),
        "quick_replies": ["Courses", "Admissions", "Fees", "Study Abroad", "Contact"]
    },

    "thanks": {
        "keywords": ["thank", "thanks", "thank you", "appreciate", "helpful", "great", "awesome",
                     "wonderful", "perfect", "excellent"],
        "response": (
            "You're very welcome! 😊\n\n"
            "Is there anything else I can help you with?\n\n"
            "Feel free to ask about our programmes, fees, or admissions anytime!"
        ),
        "quick_replies": ["More Questions", "Apply Now", "Contact Us"]
    },

    "bye": {
        "keywords": ["bye", "goodbye", "see you", "farewell", "take care", "that's all", "done",
                     "no more", "nothing else", "end chat"],
        "response": (
            "Thank you for chatting with BML College! 🎓\n\n"
            "We hope to see you as a BML student soon!\n\n"
            "📧 info@bmlcollege.com | 📞 +44 (0) 121 523 0141\n\n"
            "Have a wonderful day! 👋"
        ),
        "quick_replies": ["Apply Now", "Visit Website"]
    },

    # ── FALLBACK ──────────────────────────────────────────────────────────
    "fallback": {
        "response": (
            "I'm not quite sure about that, but I'm here to help! 😊\n\n"
            "I can assist with:\n"
            "• 📚 Courses & Programmes\n"
            "• 💰 Fees & Scholarships\n"
            "• 📝 Admissions & Applications\n"
            "• 🌍 Study Abroad\n"
            "• 🏫 Campus Information\n\n"
            "You can also speak to one of our advisors directly."
        ),
        "quick_replies": ["Courses", "Fees", "Admissions", "Talk to Agent"]
    }
}

# ── Quick reply topic map ─────────────────────────────────────────────────────
QUICK_REPLY_MAP = {
    "courses": "courses",
    "our courses": "courses",
    "countries": "destinations",
    "which countries": "destinations",
    "destinations": "destinations",
    "processing time": "timelines",
    "how long": "timelines",
    "eligibility": "eligibility",
    "requirements": "eligibility",
    "visa guarantee": "guarantees",
    "job guarantee": "guarantees",
    "dependent visa": "general_visa",
    "family visa": "general_visa",
    "business courses": "business",
    "it courses": "it_courses",
    "health courses": "health",
    "fees": "fees",
    "course fees": "fees",
    "admissions": "admissions",
    "apply now": "admissions",
    "apply": "admissions",
    "study abroad": "study_abroad",
    "contact us": "contact",
    "contact": "contact",
    "contact admissions": "contact",
    "talk to agent": "human_agent",
    "scholarships": "scholarship",
    "apply for scholarship": "scholarship",
    "lms": "lms",
    "campus": "campus",
    "accreditations": "accreditation",
    "january intake": "admissions",
    "entry requirements": "documents",
    "more questions": "welcome",
}

# ── Asiri Perera site knowledge and Ollama system prompt ──────────────────────
ASIRI_SITE_CONTEXT = """
Asiri Perera is an Academic Director at BML College, a serial entrepreneur, and a
global connector supporting students, professionals, families, and businesses.

Primary services on the website:
- Study online: UK Level 3 to Level 7 courses in business management,
  hospitality and tourism, health and social care, IT, and English. Flexible
  online study, learning materials, career-focused certification, and study
  support.
- Study abroad: personalised application support for universities in the UK,
  USA, Canada, Europe, France, Australia, New Zealand, Malta, and Malaysia.
  Includes course matching, document preparation, application guidance, and
  enrolment support.
- Work abroad: guidance for international career routes, including healthcare
  and care workers, office/admin roles, IT opportunities, construction workers,
  Middle East roles, document preparation, and application preparation.
- Recruitment for businesses: connect employers with pre-vetted workers across
  healthcare, construction, admin, hospitality, and service sectors, especially
  for UK and EU employers.
- Paralegal services: legal research, document drafting, contract review, case
  law analysis, legal correspondence, and file organisation. Do not give legal
  advice or guarantee outcomes.
- Visit visa application help: visitor/tourist visa guidance, document checklist
  support, application form preparation help, appointment guidance, and next-step
  advice. Do not guarantee visa approval.
- Free call: visitors can book a free 15-minute discovery call to decide the
  right route.

Contact details:
- WhatsApp / Sri Lanka mobile: +94 717 798989
- UK phone: +44 (0) 773 58 277 59
- Sri Lanka office: BML Sri Lanka, 163/4 New Kandy Road, Malabe, Sri Lanka
- UK office: 2nd Floor, 216A New John Street West, Hockley, Birmingham, B19 3UA,
  United Kingdom
- BML College email for college enquiries: info@bmlcollege.com

Important behaviour:
- Answer the customer's actual question first, like a helpful ChatGPT-style
  assistant.
- Use the site facts above when the question is about Asiri Perera, BML College,
  studying, work abroad, recruitment, paralegal support, visit visas, visas,
  fees, documents, offices, or booking a call.
- If a question is general and harmless, answer it normally and briefly.
- Do not invent exact fees, visa guarantees, job guarantees, university offers,
  legal advice, or scholarship promises. When details depend on the customer's
  situation, ask one useful follow-up question and suggest booking the free call.
- Keep answers concise, warm, and practical. Use bullet points only when helpful.
"""

COLLEGE_KNOWLEDGE.update({
    "welcome": {
        "response": (
            "Hi, welcome to Asiri Perera's AI assistant.\n\n"
            "I can help with study online, study abroad, work abroad, recruitment, "
            "paralegal support, visit visa help, visa/application guidance, and booking a free call.\n\n"
            "What would you like to know?"
        ),
        "quick_replies": ["Study Online", "Study Abroad", "Visit Visa", "Work Abroad", "Free Call"],
    },
    "services": {
        "keywords": [
            "services", "what can you do", "help me", "what do you offer",
            "asiri services", "support available", "how can you help"
        ],
        "response": (
            "Asiri Perera can help with five main routes: study online, study abroad, "
            "work abroad, visit visa application help, recruitment for businesses, and paralegal support. If you are "
            "not sure where to start, book a free 15-minute call on WhatsApp: +94 717 798989."
        ),
        "quick_replies": ["Study Online", "Study Abroad", "Visit Visa", "Work Abroad", "Paralegal"],
    },
    "courses": {
        "keywords": [
            "course", "courses", "programme", "program", "study", "study online",
            "online course", "uk level", "level 3", "level 4", "level 5",
            "level 6", "level 7", "business management", "hospitality",
            "tourism", "health and social care", "it course", "english course"
        ],
        "response": (
            "You can study online from UK Level 3 to Level 7 in areas such as business "
            "management, hospitality and tourism, health and social care, IT, and English. "
            "The best next step is to share your current qualification and goal so the "
            "right level can be recommended."
        ),
        "quick_replies": ["Entry Requirements", "Fees", "Study Abroad", "Free Call"],
    },
    "study_online": {
        "keywords": [
            "study online", "online study", "online programme", "online program",
            "distance learning", "level 3", "level 4", "level 5", "level 6",
            "level 7", "business course", "hospitality course", "health care course",
            "social care", "english class", "english course"
        ],
        "response": (
            "Yes. Online study is available for UK Level 3 to Level 7 routes, including "
            "business management, hospitality and tourism, health and social care, IT, "
            "and English. You can study flexibly with learning materials and support. "
            "Tell me your last qualification and preferred subject, and I can guide you."
        ),
        "quick_replies": ["Fees", "Entry Requirements", "Free Call"],
    },
    "study_abroad": {
        "keywords": [
            "study abroad", "international university", "university abroad",
            "uk university", "canada university", "usa university", "australia",
            "new zealand", "malta", "malaysia", "france", "europe", "overseas study",
            "student visa", "visa support"
        ],
        "response": (
            "Asiri can support study-abroad applications for destinations such as the UK, "
            "USA, Canada, Europe, France, Australia, New Zealand, Malta, and Malaysia. "
            "Support includes course matching, document preparation, application guidance, "
            "and enrolment support. Share your qualification, preferred country, and subject "
            "to get a clearer route."
        ),
        "quick_replies": ["Required Documents", "Fees", "Free Call", "Contact"],
    },
    "visit_visa": {
        "keywords": [
            "visit visa", "visitor visa", "tourist visa", "holiday visa",
            "travel visa", "visa application", "visit visa application",
            "visitor visa application", "tourist visa application",
            "visit visa service", "visitor visa service", "tourist visa service",
            "visa help", "visa application help", "visa form", "visa appointment",
            "embassy appointment", "travel documents", "sponsor documents",
            "invitation letter", "cover letter for visa", "visa refusal",
            "visa reapply", "re apply visa", "apply visit visa"
        ],
        "response": (
            "Yes, the team can help with visit visa application support. This can include "
            "checking the document list, preparing the application form, guidance for "
            "appointments, cover/invitation letter guidance, and next steps if you had a "
            "previous refusal. Common documents may include passport, bank statements, "
            "employment/business or study evidence, travel plan, accommodation details, "
            "and sponsor or invitation documents if relevant. Fees and processing time "
            "depend on the country and your case. Visa approval cannot be guaranteed "
            "because the embassy or immigration authority makes the decision. To guide you "
            "properly, share the country you want to visit, your passport country, travel "
            "purpose, and planned travel dates. WhatsApp: +94 717 798989."
        ),
        "quick_replies": ["Required Documents", "Free Call", "Contact"],
    },
    "destinations": {
        "keywords": [
            "countries", "which countries", "what countries", "destinations",
            "which countries can i apply", "countries can i apply",
            "where can i apply", "where can i go", "where can you send", "country list",
            "uk", "usa", "canada", "australia", "new zealand", "france",
            "malta", "malaysia", "europe", "middle east"
        ],
        "response": (
            "The team can guide routes for countries such as the UK, USA, Canada, "
            "Europe, France, Australia, New Zealand, Malta, Malaysia, and some Middle "
            "East opportunities. The best country depends on whether you want study, "
            "work, recruitment, or visit visa help. Share your goal and preferred country."
        ),
        "quick_replies": ["Study Abroad", "Work Abroad", "Visit Visa", "Free Call"],
    },
    "timelines": {
        "keywords": [
            "how long", "processing time", "time period", "duration", "how many days",
            "how many months", "when can i start", "start date", "intake",
            "how long does it take", "application time"
        ],
        "response": (
            "Timelines depend on the service and country. Online study can usually move "
            "faster once documents are ready; study abroad, work abroad, and visit visa "
            "applications depend on document preparation, provider or employer response, "
            "appointment availability, and embassy/immigration processing. Share the route "
            "and country so the team can give a realistic next step."
        ),
        "quick_replies": ["Required Documents", "Visit Visa", "Study Abroad", "Free Call"],
    },
    "eligibility": {
        "keywords": [
            "am i eligible", "eligibility", "qualify", "qualification needed",
            "requirements", "age limit", "can i apply", "without ielts",
            "no ielts", "english requirement", "minimum qualification"
        ],
        "response": (
            "Eligibility depends on the route. For study, the team checks your last "
            "qualification, English level, subject, and target country. For work or visa "
            "routes, they check your experience, documents, funds/sponsor details, and "
            "destination rules. Send your age, last qualification, English level, work "
            "experience, and target country for guidance."
        ),
        "quick_replies": ["Study Online", "Study Abroad", "Work Abroad", "Visit Visa"],
    },
    "guarantees": {
        "keywords": [
            "guarantee", "visa guarantee", "job guarantee", "sure visa",
            "guaranteed visa", "success rate", "will i get visa",
            "can you promise", "offer guarantee", "refund if refused"
        ],
        "response": (
            "No honest advisor can guarantee a visa, job, university offer, or legal "
            "outcome. The team can help prepare the application properly, check documents, "
            "and guide next steps, but the final decision is made by the embassy, employer, "
            "university, or relevant authority."
        ),
        "quick_replies": ["Required Documents", "Free Call", "Contact"],
    },
    "general_visa": {
        "keywords": [
            "dependent visa", "dependant visa", "family visa", "spouse visa",
            "immigration", "immigration help", "visa advice", "visa guidance",
            "visa service", "refused visa", "visa refusal", "appeal visa"
        ],
        "response": (
            "The team can discuss visa guidance and document/application support, including "
            "visit visa help and general next-step guidance for other visa routes. For "
            "regulated immigration or legal advice, you may need a qualified adviser or "
            "lawyer. Share the visa type, country, refusal history if any, and your goal."
        ),
        "quick_replies": ["Visit Visa", "Required Documents", "Free Call", "Contact"],
    },
    "work_abroad": {
        "keywords": [
            "work abroad", "job abroad", "overseas job", "work visa", "care job",
            "healthcare job", "construction job", "middle east job", "admin job",
            "office job", "it job", "international career", "apply for work"
        ],
        "response": (
            "Work-abroad guidance is available for routes such as healthcare/care, office "
            "and admin, IT, construction, and Middle East opportunities. The support can "
            "include document preparation and application guidance, but job or visa outcomes "
            "cannot be guaranteed. Tell me your experience, target country, and role."
        ),
        "quick_replies": ["Required Documents", "Free Call", "Contact"],
    },
    "recruitment": {
        "keywords": [
            "recruit", "recruitment", "hire workers", "find workers", "staffing",
            "manpower", "vacancy", "employer", "candidate", "healthcare workers",
            "construction workers", "admin staff", "hospitality workers"
        ],
        "response": (
            "Businesses can get recruitment support for pre-vetted candidates across "
            "healthcare, construction, admin, hospitality, and service roles. Share the job "
            "title, location, number of workers, required skills, and start date so the team "
            "can assess the vacancy."
        ),
        "quick_replies": ["Share Vacancy", "Free Call", "Contact"],
    },
    "paralegal": {
        "keywords": [
            "paralegal", "legal", "legal support", "legal document", "drafting",
            "contract review", "legal research", "case law", "correspondence",
            "file organisation", "file organization"
        ],
        "response": (
            "Paralegal support can include legal research, document drafting, contract "
            "review, case law analysis, legal correspondence, and file organisation. For "
            "legal advice or decisions, you should speak with a qualified lawyer. Tell me "
            "what document or task you need help with."
        ),
        "quick_replies": ["Free Call", "Contact"],
    },
    "admissions": {
        "keywords": [
            "admission", "apply", "application", "enrol", "enroll", "register",
            "entry requirement", "eligibility", "how to join", "intake", "start course"
        ],
        "response": (
            "Application steps depend on the route: online study, study abroad, or work "
            "abroad. Usually the team needs your current qualification, passport/ID details, "
            "academic documents, preferred subject or country, and contact details. Share "
            "your goal and I can guide the next step."
        ),
        "quick_replies": ["Study Online", "Study Abroad", "Required Documents", "Free Call"],
    },
    "documents": {
        "keywords": [
            "document", "documents", "passport", "certificate", "transcript", "cv",
            "resume", "english proof", "ielts", "qualification", "personal statement",
            "reference", "upload"
        ],
        "response": (
            "Common documents include passport or ID, academic certificates/transcripts, "
            "CV if applying for work, English proof if required, and any destination-specific "
            "forms. For visit visas, documents may also include bank statements, employment "
            "or business evidence, accommodation/travel plans, invitation or sponsor details "
            "where relevant, and previous refusal details if any. Exact documents depend on "
            "your service, country, and personal situation."
        ),
        "quick_replies": ["Study Abroad", "Work Abroad", "Free Call"],
    },
    "fees": {
        "keywords": [
            "fee", "fees", "cost", "price", "tuition", "how much", "payment",
            "installment", "instalment", "scholarship", "discount"
        ],
        "response": (
            "Fees depend on the service, programme level, destination, and application route. "
            "For an accurate quote, share whether you want study online, study abroad, work "
            "abroad, recruitment, or paralegal support, plus your target country or course."
        ),
        "quick_replies": ["Study Online", "Study Abroad", "Free Call", "Contact"],
    },
    "contact": {
        "keywords": [
            "contact", "phone", "email", "call", "whatsapp", "book call", "free call",
            "appointment", "office", "address", "where are you"
        ],
        "response": (
            "You can book a free 15-minute call on WhatsApp: +94 717 798989. "
            "UK phone: +44 (0) 773 58 277 59. UK office: 2nd Floor, 216A New John "
            "Street West, Hockley, Birmingham, B19 3UA. Sri Lanka office: 163/4 New "
            "Kandy Road, Malabe."
        ),
        "quick_replies": ["Free Call", "Services", "Study Abroad"],
    },
    "fallback": {
        "response": (
            "I can help with study online, study abroad, visit visa applications, work abroad, "
            "recruitment, paralegal support, documents, fees, and booking a free call. Could you "
            "tell me a little more about what you want to do?"
        ),
        "quick_replies": ["Services", "Study Online", "Study Abroad", "Work Abroad", "Free Call"],
    },
})


COLLEGE_KNOWLEDGE.update({
    "about": {
        "keywords": [
            "about", "who are you", "what is asiri", "who is asiri",
            "tell me about asiri", "tell me about", "history", "background"
        ],
        "response": (
            "Asiri Perera supports students, professionals, families, and businesses "
            "through online study, study abroad, work abroad, recruitment, and paralegal "
            "support. He is connected with BML College and helps visitors choose the right "
            "route based on their goal."
        ),
        "quick_replies": ["Services", "Study Online", "Study Abroad", "Work Abroad", "Free Call"],
    },
    "business": {
        "keywords": [
            "business", "business course", "business management", "mba",
            "management", "marketing", "finance", "accounting", "commerce"
        ],
        "response": (
            "Business and management study routes are available online from UK Level 3 "
            "to Level 7. The right level depends on your current qualification and whether "
            "you want career progress, a top-up route, or postgraduate study."
        ),
        "quick_replies": ["Entry Requirements", "Fees", "Study Online", "Free Call"],
    },
    "it_courses": {
        "keywords": [
            "computer", "technology", "software", "programming",
            "information technology", "it course", "cyber", "networking",
            "data science", "ai", "computing"
        ],
        "response": (
            "IT-related online study and international routes may be available depending "
            "on your level and target country. Share your current qualification, preferred "
            "area such as software, networking, or data, and whether you want study or work "
            "guidance."
        ),
        "quick_replies": ["Study Online", "Study Abroad", "Work Abroad", "Free Call"],
    },
    "health": {
        "keywords": [
            "health", "health care", "healthcare", "nursing", "medical",
            "social care", "health and social care", "health care course",
            "healthcare course", "health and social care course"
        ],
        "response": (
            "Health and social care support can cover online study routes and work-abroad "
            "preparation for suitable healthcare or care roles. Outcomes depend on your "
            "experience, documents, destination, and employer or visa requirements."
        ),
        "quick_replies": ["Study Online", "Work Abroad", "Required Documents", "Free Call"],
    },
    "scholarship": {
        "keywords": [
            "scholarship", "grant", "bursary", "financial aid", "discount",
            "reduced fee"
        ],
        "response": (
            "Scholarships or discounts depend on the specific programme, destination, "
            "intake, and provider rules. Share the course or country you are interested in "
            "so the team can check what is currently available."
        ),
        "quick_replies": ["Fees", "Study Online", "Study Abroad", "Free Call"],
    },
    "campus": {
        "keywords": [
            "campus", "location", "address", "where", "office", "birmingham",
            "malabe", "sri lanka", "hockley", "find you", "directions"
        ],
        "response": (
            "UK office: 2nd Floor, 216A New John Street West, Hockley, Birmingham, "
            "B19 3UA. Sri Lanka office: 163/4 New Kandy Road, Malabe. You can also "
            "contact WhatsApp on +94 717 798989 or UK phone +44 (0) 773 58 277 59."
        ),
        "quick_replies": ["Free Call", "Contact", "Services"],
    },
    "accreditation": {
        "keywords": [
            "accredit", "recognised", "recognized", "valid", "legit",
            "approved", "othm", "ofqual", "quality", "regulated"
        ],
        "response": (
            "Recognition and accreditation depend on the exact course, level, awarding "
            "body, and study route. Share the programme name or level you are checking, "
            "and the team can confirm the correct awarding or recognition details."
        ),
        "quick_replies": ["Courses", "Study Online", "Free Call"],
    },
    "lms": {
        "keywords": [
            "lms", "portal", "login", "online portal", "student portal",
            "e-learning", "elearning", "access", "password", "account",
            "log in", "sign in"
        ],
        "response": (
            "For online study access or portal help, contact the team with your full name, "
            "course, and registered email. WhatsApp: +94 717 798989. College enquiries can "
            "also use info@bmlcollege.com."
        ),
        "quick_replies": ["Contact", "Study Online"],
    },
    "human_agent": {
        "keywords": [
            "human", "agent", "person", "staff", "advisor", "counsellor",
            "counselor", "speak to someone", "talk to someone", "real person",
            "live chat", "call me", "callback"
        ],
        "response": (
            "You can speak with the team directly on WhatsApp: +94 717 798989. "
            "UK phone: +44 (0) 773 58 277 59. You can also ask to book the free "
            "15-minute discovery call."
        ),
        "quick_replies": ["Free Call", "Services", "Contact"],
    },
    "alumni": {
        "keywords": ["alumni", "graduate", "former student", "past student", "alumni network"],
        "response": (
            "For graduate or alumni-related questions, share whether you need study "
            "progression, work-abroad guidance, document support, or a reference-style "
            "enquiry, and the team can direct you."
        ),
        "quick_replies": ["Study Abroad", "Work Abroad", "Contact"],
    },
    "junior": {
        "keywords": ["junior", "montessori", "daycare", "day care", "nursery", "child", "kids"],
        "response": (
            "I do not have confirmed childcare or junior programme details in the current "
            "site information. Please contact the team on WhatsApp +94 717 798989 so they "
            "can confirm the latest options."
        ),
        "quick_replies": ["Contact", "Services"],
    },
    "greeting": {
        "keywords": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"],
        "response": (
            "Hello, welcome to Asiri Perera's AI assistant. I can help with study online, "
            "study abroad, work abroad, recruitment, paralegal support, documents, fees, "
            "and booking a free call."
        ),
        "quick_replies": ["Services", "Study Online", "Study Abroad", "Work Abroad", "Free Call"],
    },
    "thanks": {
        "keywords": ["thank", "thanks", "thank you", "appreciate", "helpful", "great"],
        "response": (
            "You're welcome. If you want, I can also help you choose the right route or "
            "connect you with the team for a free 15-minute call."
        ),
        "quick_replies": ["Services", "Free Call", "Contact"],
    },
    "bye": {
        "keywords": ["bye", "goodbye", "see you", "take care", "done", "end chat"],
        "response": (
            "Thanks for chatting with Asiri Perera's assistant. For direct help, WhatsApp "
            "+94 717 798989 or call the UK number +44 (0) 773 58 277 59."
        ),
        "quick_replies": ["Free Call", "Contact"],
    },
})

QUICK_REPLY_MAP.update({
    "visit visa": "visit_visa",
    "visitor visa": "visit_visa",
    "tourist visa": "visit_visa",
    "visit visa service": "visit_visa",
    "visa application": "visit_visa",
    "visa help": "visit_visa",
    "business courses": "business",
    "it courses": "it_courses",
    "health courses": "health",
    "campus": "campus",
    "office": "campus",
    "location": "campus",
    "human agent": "human_agent",
    "talk to human": "human_agent",
    "talk to agent": "human_agent",
    "scholarships": "scholarship",
    "lms": "lms",
    "student portal": "lms",
    "accreditations": "accreditation",
    "services": "services",
    "study online": "study_online",
    "online study": "study_online",
    "study abroad": "study_abroad",
    "work abroad": "work_abroad",
    "recruitment": "recruitment",
    "recruit workers": "recruitment",
    "paralegal": "paralegal",
    "free call": "contact",
    "book a free call": "contact",
    "book call": "contact",
    "required documents": "documents",
    "share vacancy": "recruitment",
})


# Final support-flow training: welcome options, visa services, and fallback guidance.
COLLEGE_KNOWLEDGE.update({
    "welcome": {
        "response": (
            "Welcome to the Asiri Perera Global Services AI Assistant.\n\n"
            "Please choose an option below, or type your own question. I can help with "
            "study online, study abroad, visa services, work abroad, recruitment, "
            "paralegal support, documents, fees, and booking a free call.\n\n"
            "If I cannot answer confidently, I will connect you to an advisor."
        ),
        "quick_replies": [
            "Study Online", "Study Abroad", "Visa Services",
            "Work Abroad", "Recruitment", "Talk to Agent"
        ],
    },
    "services": {
        "keywords": [
            "services", "what can you do", "help me", "what do you offer",
            "asiri services", "support available", "how can you help"
        ],
        "response": (
            "Asiri Perera can help with study online, study abroad, visa services "
            "including visit visa application support, work abroad guidance, recruitment "
            "for businesses, and paralegal support. Choose an option or type your question."
        ),
        "quick_replies": [
            "Study Online", "Study Abroad", "Visa Services",
            "Work Abroad", "Recruitment", "Free Call"
        ],
    },
    "general_visa": {
        "keywords": [
            "visa services", "visa service", "visa support", "visa guidance",
            "visa consultation", "visa advice", "visa help", "visa application",
            "visit visa", "visitor visa", "tourist visa", "dependent visa",
            "dependant visa", "family visa", "spouse visa", "immigration help",
            "visa documents", "visa appointment", "visa refusal"
        ],
        "response": (
            "Yes, visa services are available. The team can help with visit visa "
            "application support, document checklists, form preparation guidance, "
            "appointment guidance, cover or invitation letter guidance, and general "
            "next-step advice for other visa routes. Visa approval cannot be guaranteed "
            "because the final decision is made by the embassy or immigration authority. "
            "Please share the country, visa type, passport country, and travel purpose."
        ),
        "quick_replies": ["Visit Visa", "Required Documents", "Free Call", "Contact"],
    },
    "greeting": {
        "keywords": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"],
        "response": (
            "Welcome to the Asiri Perera Global Services AI Assistant. Please choose an "
            "option below, or type your question. If I cannot answer confidently, I will "
            "connect you to an advisor."
        ),
        "quick_replies": [
            "Study Online", "Study Abroad", "Visa Services",
            "Work Abroad", "Recruitment", "Talk to Agent"
        ],
    },
    "fallback": {
        "response": (
            "I can try to answer general questions, but I am not fully confident about "
            "that one. I can connect you to an advisor for accurate help."
        ),
        "quick_replies": ["Visa Services", "Study Abroad", "Work Abroad", "Talk to Agent"],
    },
})

QUICK_REPLY_MAP.update({
    "visa services": "general_visa",
    "visa service": "general_visa",
    "visa support": "general_visa",
    "visa guidance": "general_visa",
    "visa consultation": "general_visa",
    "visa documents": "general_visa",
    "talk to agent": "human_agent",
})

OLLAMA_SYSTEM_PROMPT = f"""You are Asiri Perera's AI chat assistant for website visitors.

Your job is to answer like a helpful ChatGPT-style support assistant while using
the website facts below as your source of truth for Asiri Perera, BML College,
study routes, work routes, recruitment, paralegal support, documents, fees, and
contact details.

{ASIRI_SITE_CONTEXT}

Response rules:
1. Answer the customer's exact question first.
2. Be natural, warm, and practical.
3. For service questions, give clear next steps and ask for the one missing
   detail that would help most.
4. If the customer asks a general harmless question, answer it normally.
5. If details are uncertain, say so and offer the free call instead of guessing.
6. Never promise visas, jobs, scholarships, university offers, legal outcomes, or
   exact fees unless the user provided official confirmed information.
"""
