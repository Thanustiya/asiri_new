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

# ── Ollama system prompt ───────────────────────────────────────────────────────
OLLAMA_SYSTEM_PROMPT = """You are the AI assistant for BML College UK & International, a prestigious college established in 2012, headquartered in Birmingham, UK with a campus in Malabe, Sri Lanka.

IMPORTANT RULES:
1. Keep answers SHORT and SIMPLE (max 3-4 sentences)
2. Always be friendly and professional
3. Only answer questions about BML College
4. If asked something outside BML College topics, politely redirect
5. Never make up information - stick to facts

KEY FACTS:
- Founded: 2012 | Location: Birmingham, UK & Malabe, Sri Lanka
- Phone UK: +44 (0) 121 523 0141 | Email: info@bmlcollege.com
- 97% success rate | 1000+ students | 39+ programmes
- Programmes: Business, IT, Health, Psychology, Law, Education, Engineering, Languages, Hospitality
- Accreditations: OTHM, UKRLP, Microsoft Partner, British Council, ICO
- Study abroad: UK, Australia, Canada, USA, Europe
- LMS: bmlcollege.com/connect | Portal: cms.bmlcollege.com

Answer in a warm, helpful tone. Be concise."""