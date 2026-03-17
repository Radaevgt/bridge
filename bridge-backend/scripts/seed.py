"""Seed script for demo data. Run: python scripts/seed.py [--reset]"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent dir to path so we can import app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func as sqlfunc, select, text

from app.database import async_session
from app.models.chat import ChatRoom, Message
from app.models.review import Review
from app.models.specialist import (
    Availability,
    LanguageProficiency,
    SpecialistCompetency,
    SpecialistDomain,
    SpecialistLanguage,
    SpecialistProfile,
)
from app.models.task_request import RequestStatus, TaskProposal, TaskRequest, Urgency
from app.models.user import User, UserRole
from app.utils.security import hash_password

PASSWORD = hash_password("Demo1234!")

AVAIL = {
    "available": Availability.AVAILABLE,
    "busy": Availability.BUSY,
    "vacation": Availability.VACATION,
}

# ══════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════

# ── Clients (18) ─────────────────────────────────────────────────────
CLIENTS_DATA = [
    ("Alice Johnson", "client@demo.com"),
    ("Bob Smith", "bob@demo.com"),
    ("Carol White", "carol@demo.com"),
    ("Dave Brown", "dave@demo.com"),
    ("Eve Davis", "eve@demo.com"),
    ("Frank Wilson", "frank@demo.com"),
    ("Grace Lee", "grace@demo.com"),
    ("Henry Martinez", "henry@demo.com"),
    ("Ivy Clark", "ivy@demo.com"),
    ("Jack Turner", "jack@demo.com"),
    ("Kenji Yamamoto", "kenji@demo.com"),
    ("Luna Reyes", "luna@demo.com"),
    ("Marcus Cole", "marcus@demo.com"),
    ("Nadia Hussain", "nadia@demo.com"),
    ("Oliver Berg", "oliver@demo.com"),
    ("Priya Nair", "priya.nair@demo.com"),
    ("Tomasz Kowalski", "tomasz@demo.com"),
    ("Zara Okonkwo", "zara@demo.com"),
]

# ── Specialists (45) ────────────────────────────────────────────────
SPECIALISTS_DATA = [
    # 0
    {
        "name": "Dr. Sarah Chen",
        "email": "expert@demo.com",
        "headline": "AI/ML Research Consultant",
        "bio": "PhD in Machine Learning from Stanford with 10 years of experience in NLP, computer vision, and deep learning. Published 30+ papers in top conferences. Previously led ML teams at Google and Meta.",
        "rate": 150.0, "availability": "available",
        "domains": ["AI/ML", "Science"],
        "languages": [("English", "native"), ("Mandarin", "native")],
        "competencies": [
            ("Stanford PhD Thesis", "https://arxiv.org/example"),
            ("Google AI Blog", "https://ai.google/research"),
            ("NeurIPS 2024 Paper", "https://neurips.cc/example"),
        ],
    },
    # 1
    {
        "name": "Prof. James Miller",
        "email": "james@demo.com",
        "headline": "Corporate Law Expert",
        "bio": "Former partner at Baker McKenzie. 20 years specializing in M&A, corporate governance, and international trade law. Advised on $5B+ in transactions.",
        "rate": 250.0, "availability": "available",
        "domains": ["Law", "Business"],
        "languages": [("English", "native")],
        "competencies": [
            ("Baker McKenzie Profile", "https://bakermckenzie.com/example"),
            ("Harvard Law Review", "https://harvardlawreview.org/example"),
        ],
    },
    # 2
    {
        "name": "Maria Garcia",
        "email": "maria@demo.com",
        "headline": "Financial Planning Advisor",
        "bio": "Certified Financial Planner (CFP) with 15 years of experience. Specializes in retirement planning, tax optimization, and wealth management for high-net-worth individuals.",
        "rate": 120.0, "availability": "busy",
        "domains": ["Finance", "Business"],
        "languages": [("English", "fluent"), ("Spanish", "native")],
        "competencies": [
            ("CFP Certification", "https://cfp.net/verify"),
            ("Forbes Finance Column", "https://forbes.com/example"),
        ],
    },
    # 3
    {
        "name": "Dr. Robert Kim",
        "email": "robert@demo.com",
        "headline": "Data Science Mentor",
        "bio": "Lead data scientist at Amazon. PhD in Statistics from MIT. Mentor for aspiring data professionals. Expert in A/B testing, causal inference, and ML ops.",
        "rate": 100.0, "availability": "available",
        "domains": ["AI/ML", "Science"],
        "languages": [("English", "native"), ("Korean", "fluent")],
        "competencies": [
            ("MIT Statistics PhD", "https://mit.edu/example"),
            ("Kaggle Grandmaster", "https://kaggle.com/example"),
            ("AWS ML Specialty", "https://aws.amazon.com/cert"),
        ],
    },
    # 4
    {
        "name": "Lisa Thompson",
        "email": "lisa@demo.com",
        "headline": "UX/UI Design Consultant",
        "bio": "Award-winning designer with 8 years of experience at Apple and Airbnb. Specializes in mobile-first design, design systems, and user research.",
        "rate": 90.0, "availability": "available",
        "domains": ["Design"],
        "languages": [("English", "native")],
        "competencies": [
            ("Dribbble Portfolio", "https://dribbble.com/example"),
            ("Behance Showcase", "https://behance.net/example"),
            ("Apple Design Award", "https://developer.apple.com/design"),
        ],
    },
    # 5
    {
        "name": "Ahmed Hassan",
        "email": "ahmed@demo.com",
        "headline": "Cybersecurity Specialist",
        "bio": "CISSP and OSCP certified. 12 years in infosec. Conducts penetration testing, security audits, and incident response for Fortune 500 companies.",
        "rate": 200.0, "availability": "available",
        "domains": ["Engineering", "Science"],
        "languages": [("English", "fluent"), ("Arabic", "native")],
        "competencies": [
            ("CISSP Certification", "https://isc2.org/verify"),
            ("OSCP Badge", "https://offensive-security.com"),
            ("DEF CON Speaker", "https://defcon.org/example"),
        ],
    },
    # 6
    {
        "name": "Dr. Emily Watson",
        "email": "emily@demo.com",
        "headline": "Biotech Research Advisor",
        "bio": "Published researcher in gene therapy and molecular biology at Johns Hopkins. Holds 3 patents in CRISPR applications. Consults for pharma startups.",
        "rate": 180.0, "availability": "vacation",
        "domains": ["Medicine", "Science"],
        "languages": [("English", "native"), ("German", "fluent")],
        "competencies": [
            ("CRISPR Patent", "https://patents.google.com/example"),
            ("Nature Publication", "https://nature.com/example"),
        ],
    },
    # 7
    {
        "name": "Michael Chang",
        "email": "michael@demo.com",
        "headline": "Startup Strategy Coach",
        "bio": "Serial entrepreneur who has founded 4 companies and raised $50M+ in venture capital. Y Combinator alum. Advisor to 20+ early-stage startups.",
        "rate": 300.0, "availability": "available",
        "domains": ["Business"],
        "languages": [("English", "native"), ("Mandarin", "conversational")],
        "competencies": [
            ("Y Combinator Profile", "https://ycombinator.com/example"),
            ("TechCrunch Feature", "https://techcrunch.com/example"),
            ("Crunchbase", "https://crunchbase.com/example"),
        ],
    },
    # 8
    {
        "name": "Sofia Rossi",
        "email": "sofia@demo.com",
        "headline": "Academic Writing Tutor",
        "bio": "PhD in Linguistics from Oxford. Helps graduate students with thesis writing, research methodology, and academic publishing. 500+ students mentored.",
        "rate": 60.0, "availability": "available",
        "domains": ["Education"],
        "languages": [("English", "fluent"), ("Italian", "native")],
        "competencies": [
            ("Oxford PhD", "https://ox.ac.uk/example"),
            ("Published Book", "https://amazon.com/example"),
        ],
    },
    # 9
    {
        "name": "Daniel Okafor",
        "email": "daniel@demo.com",
        "headline": "Cloud Architecture Consultant",
        "bio": "AWS Solutions Architect Professional. Designs scalable cloud infrastructure for enterprises. Previously at Microsoft Azure team.",
        "rate": 175.0, "availability": "available",
        "domains": ["Engineering"],
        "languages": [("English", "fluent"), ("Yoruba", "native")],
        "competencies": [
            ("AWS SA Professional", "https://aws.amazon.com/cert"),
            ("Microsoft MVP", "https://mvp.microsoft.com/example"),
            ("GitHub Profile", "https://github.com/example"),
        ],
    },
    # 10
    {
        "name": "Dr. Yuki Tanaka",
        "email": "yuki@demo.com",
        "headline": "Medical Research Consultant",
        "bio": "MD from Tokyo University, specializing in clinical trials and epidemiology. 15 years of experience in pharmaceutical research and public health.",
        "rate": 220.0, "availability": "available",
        "domains": ["Medicine", "Science"],
        "languages": [("English", "fluent"), ("Japanese", "native")],
        "competencies": [
            ("Tokyo University MD", "https://u-tokyo.ac.jp/example"),
            ("WHO Consultant", "https://who.int/example"),
        ],
    },
    # 11
    {
        "name": "Carlos Rivera",
        "email": "carlos@demo.com",
        "headline": "Digital Marketing Strategist",
        "bio": "Former CMO of a $100M SaaS company. Expert in growth hacking, SEO, paid acquisition, and brand strategy. Managed $20M+ in ad spend.",
        "rate": 130.0, "availability": "available",
        "domains": ["Marketing", "Business"],
        "languages": [("English", "native"), ("Spanish", "fluent")],
        "competencies": [
            ("Google Analytics Certified", "https://skillshop.google.com/example"),
            ("HubSpot Academy", "https://academy.hubspot.com/example"),
        ],
    },
    # 12
    {
        "name": "Dr. Anna Petrov",
        "email": "anna@demo.com",
        "headline": "Mechanical Engineering Advisor",
        "bio": "PhD in Mechanical Engineering from ETH Zurich. Specializes in robotics, CAD/CAM, and manufacturing optimization. 20+ patents.",
        "rate": 160.0, "availability": "busy",
        "domains": ["Engineering"],
        "languages": [("English", "fluent"), ("Russian", "native")],
        "competencies": [
            ("ETH Zurich PhD", "https://ethz.ch/example"),
            ("Patent Portfolio", "https://patents.google.com/example"),
        ],
    },
    # 13
    {
        "name": "Thomas Burke",
        "email": "thomas@demo.com",
        "headline": "Business English Coach",
        "bio": "CELTA-certified English teacher with 10 years experience. Specializes in business English, presentation skills, and cross-cultural communication.",
        "rate": 45.0, "availability": "available",
        "domains": ["Education"],
        "languages": [("English", "native")],
        "competencies": [
            ("CELTA Certificate", "https://cambridgeenglish.org/example"),
            ("Published Textbook", "https://amazon.com/example"),
            ("YouTube Channel", "https://youtube.com/example"),
        ],
    },
    # 14
    {
        "name": "Nina Johansson",
        "email": "nina@demo.com",
        "headline": "Sustainability Consultant",
        "bio": "MSc in Environmental Science. Helps companies develop ESG strategies, carbon footprint reduction plans, and sustainability reports.",
        "rate": 110.0, "availability": "available",
        "domains": ["Science", "Other"],
        "languages": [("English", "fluent"), ("Swedish", "native")],
        "competencies": [
            ("MSc Environmental Science", "https://university.edu/example"),
            ("UN Climate Report", "https://unfccc.int/example"),
        ],
    },
    # 15
    {
        "name": "Raj Patel",
        "email": "raj@demo.com",
        "headline": "Full-Stack Development Mentor",
        "bio": "Senior engineer at Netflix. 12 years of experience in React, Node.js, Python, and distributed systems. Open-source contributor.",
        "rate": 85.0, "availability": "available",
        "domains": ["Engineering"],
        "languages": [("English", "native"), ("Hindi", "native")],
        "competencies": [
            ("Netflix Engineering Blog", "https://netflixtechblog.com/example"),
            ("GitHub 5K+ Stars", "https://github.com/example"),
            ("React Conf Speaker", "https://conf.react.dev/example"),
        ],
    },
    # 16
    {
        "name": "Dr. Laura Santos",
        "email": "laura@demo.com",
        "headline": "Psychology & Coaching Expert",
        "bio": "Licensed clinical psychologist and executive coach. PhD from Columbia University. Specializes in cognitive behavioral therapy and leadership development.",
        "rate": 140.0, "availability": "available",
        "domains": ["Other"],
        "languages": [("English", "native"), ("Spanish", "conversational")],
        "competencies": [
            ("Columbia PhD", "https://columbia.edu/example"),
            ("Published Research", "https://apa.org/example"),
        ],
    },
    # 17
    {
        "name": "Omar Farid",
        "email": "omar@demo.com",
        "headline": "Blockchain & Web3 Consultant",
        "bio": "Early Ethereum contributor. Built 10+ DeFi protocols. Expert in Solidity, smart contract auditing, and tokenomics design.",
        "rate": 190.0, "availability": "available",
        "domains": ["Finance", "Engineering"],
        "languages": [("English", "fluent"), ("Arabic", "native"), ("French", "fluent")],
        "competencies": [
            ("Ethereum Foundation Grant", "https://ethereum.org/example"),
            ("Solidity Auditor", "https://code4rena.com/example"),
        ],
    },
    # 18
    {
        "name": "Dr. Mei Lin",
        "email": "mei@demo.com",
        "headline": "Chemistry Tutor & Research Advisor",
        "bio": "Associate Professor of Organic Chemistry at UC Berkeley. Author of 50+ peer-reviewed papers. Passionate about making chemistry accessible.",
        "rate": 95.0, "availability": "available",
        "domains": ["Science", "Education"],
        "languages": [("English", "native"), ("Mandarin", "native")],
        "competencies": [
            ("UC Berkeley Faculty", "https://berkeley.edu/example"),
            ("ACS Publications", "https://pubs.acs.org/example"),
        ],
    },
    # 19
    {
        "name": "Patrick O'Brien",
        "email": "patrick@demo.com",
        "headline": "Music Theory & Composition Teacher",
        "bio": "Berklee College of Music graduate. Film score composer with credits on 15+ feature films. Teaches music theory, composition, and production.",
        "rate": 70.0, "availability": "available",
        "domains": ["Other"],
        "languages": [("English", "native")],
        "competencies": [
            ("Berklee Diploma", "https://berklee.edu/example"),
            ("IMDB Credits", "https://imdb.com/example"),
            ("Spotify Artist", "https://open.spotify.com/example"),
        ],
    },
    # 20
    {
        "name": "Fatima Al-Rashid",
        "email": "fatima@demo.com",
        "headline": "International Trade Specialist",
        "bio": "15 years in international commerce. Expert in import/export regulations, customs compliance, and trade finance. Fluent in 4 languages.",
        "rate": 155.0, "availability": "available",
        "domains": ["Law", "Business"],
        "languages": [("English", "fluent"), ("Arabic", "native"), ("French", "native")],
        "competencies": [
            ("ICC Arbitration Experience", "https://iccwbo.org/example"),
            ("Trade Finance Certificate", "https://tradefi.org/example"),
        ],
    },
    # 21
    {
        "name": "Viktor Novak",
        "email": "viktor@demo.com",
        "headline": "Fitness & Nutrition Coach",
        "bio": "Certified personal trainer (NASM) and sports nutritionist. Former Olympic athlete. Helps clients achieve peak performance through science-based methods.",
        "rate": 50.0, "availability": "available",
        "domains": ["Other"],
        "languages": [("English", "fluent"), ("Czech", "native"), ("German", "fluent")],
        "competencies": [
            ("NASM Certification", "https://nasm.org/verify"),
            ("Olympic Record", "https://olympics.com/example"),
            ("Precision Nutrition", "https://precisionnutrition.com/example"),
        ],
    },
    # 22
    {
        "name": "Priya Sharma",
        "email": "priya@demo.com",
        "headline": "Data Visualization Expert",
        "bio": "Senior data analyst at The New York Times. Expert in D3.js, Tableau, and storytelling with data. Created visualizations seen by millions.",
        "rate": 80.0, "availability": "available",
        "domains": ["AI/ML", "Design"],
        "languages": [("English", "fluent"), ("Hindi", "native")],
        "competencies": [
            ("NYT Visualization Portfolio", "https://nytimes.com/interactive"),
            ("D3.js Conference Talk", "https://d3js.org/example"),
        ],
    },
    # 23
    {
        "name": "Hans Mueller",
        "email": "hans@demo.com",
        "headline": "German Language & Culture Tutor",
        "bio": "Native German speaker with MA in German Studies. 8 years teaching German as a foreign language. Specializes in B1-C2 levels and business German.",
        "rate": 55.0, "availability": "available",
        "domains": ["Education"],
        "languages": [("English", "fluent"), ("German", "native")],
        "competencies": [
            ("Goethe-Institut Certification", "https://goethe.de/example"),
            ("German Studies MA", "https://university.de/example"),
        ],
    },
    # 24
    {
        "name": "Aisha Obi",
        "email": "aisha@demo.com",
        "headline": "Photography & Visual Arts Mentor",
        "bio": "Award-winning photojournalist. Published in National Geographic and TIME. Teaches composition, lighting, post-processing, and visual storytelling.",
        "rate": 65.0, "availability": "vacation",
        "domains": ["Design", "Other"],
        "languages": [("English", "fluent"), ("Yoruba", "native"), ("French", "conversational")],
        "competencies": [
            ("National Geographic Published", "https://natgeo.com/example"),
            ("TIME Photo Award", "https://time.com/example"),
        ],
    },
    # ── NEW SPECIALISTS (25-44) ──────────────────────────────────────
    # 25
    {
        "name": "Dr. Svetlana Kozlova",
        "email": "svetlana@demo.com",
        "headline": "Biostatistics & Epidemiology Expert",
        "bio": "PhD in Biostatistics from Harvard School of Public Health. 10 years designing clinical trials for pharmaceutical companies. WHO advisor on vaccine efficacy studies.",
        "rate": 195.0, "availability": "available",
        "domains": ["Medicine", "Science"],
        "languages": [("English", "fluent"), ("Russian", "native"), ("French", "conversational")],
        "competencies": [
            ("Harvard SPH PhD", "https://hsph.harvard.edu/example"),
            ("Lancet Publication", "https://thelancet.com/example"),
            ("WHO Advisory Board", "https://who.int/advisory"),
        ],
    },
    # 26
    {
        "name": "Liam O'Connor",
        "email": "liam@demo.com",
        "headline": "Intellectual Property Lawyer",
        "bio": "Partner at a top IP boutique firm in London. 14 years handling patent litigation, trademark disputes, and licensing agreements across tech and pharma sectors.",
        "rate": 280.0, "availability": "available",
        "domains": ["Law"],
        "languages": [("English", "native")],
        "competencies": [
            ("UK Solicitors Roll", "https://sra.org.uk/example"),
            ("EPO Patent Attorney", "https://epo.org/example"),
            ("IAM Patent 1000", "https://iam-media.com/example"),
        ],
    },
    # 27
    {
        "name": "Chen Wei",
        "email": "chenwei@demo.com",
        "headline": "Quantitative Finance Analyst",
        "bio": "Former quant at Goldman Sachs. PhD in Financial Mathematics from Princeton. Builds algorithmic trading strategies and risk models for hedge funds.",
        "rate": 275.0, "availability": "busy",
        "domains": ["Finance"],
        "languages": [("English", "fluent"), ("Mandarin", "native")],
        "competencies": [
            ("Princeton PhD", "https://princeton.edu/example"),
            ("CFA Charterholder", "https://cfainstitute.org/example"),
            ("QuantNet Contributor", "https://quantnet.com/example"),
        ],
    },
    # 28
    {
        "name": "Isabella Fernandez",
        "email": "isabella@demo.com",
        "headline": "Brand Strategy & Content Marketing",
        "bio": "Built brand strategies for Nike, Spotify, and 30+ startups. Expert in storytelling, social media campaigns, and influencer partnerships. TEDx speaker.",
        "rate": 145.0, "availability": "available",
        "domains": ["Marketing"],
        "languages": [("English", "native"), ("Spanish", "native"), ("Portuguese", "conversational")],
        "competencies": [
            ("TEDx Talk", "https://ted.com/example"),
            ("Adweek Feature", "https://adweek.com/example"),
            ("Cannes Lions Shortlist", "https://canneslions.com/example"),
        ],
    },
    # 29
    {
        "name": "Dr. Benjamin Osei",
        "email": "benjamin@demo.com",
        "headline": "Renewable Energy Engineer",
        "bio": "PhD in Electrical Engineering from TU Munich. Specializes in solar PV system design, grid integration, and energy storage. Led 15 utility-scale projects across Africa.",
        "rate": 135.0, "availability": "available",
        "domains": ["Engineering", "Science"],
        "languages": [("English", "fluent"), ("German", "fluent"), ("Twi", "native")],
        "competencies": [
            ("TU Munich PhD", "https://tum.de/example"),
            ("IEEE Publication", "https://ieee.org/example"),
            ("Solar Energy Society Fellow", "https://ises.org/example"),
        ],
    },
    # 30
    {
        "name": "Natasha Volkov",
        "email": "natasha@demo.com",
        "headline": "Product Design Lead",
        "bio": "Head of Design at a Series B fintech startup. Previously at Figma and Stripe. Specializes in design systems, prototyping, and design-to-dev handoff.",
        "rate": 115.0, "availability": "busy",
        "domains": ["Design", "Engineering"],
        "languages": [("English", "fluent"), ("Russian", "native"), ("Ukrainian", "native")],
        "competencies": [
            ("Figma Community Creator", "https://figma.com/@example"),
            ("Awwwards Winner", "https://awwwards.com/example"),
        ],
    },
    # 31
    {
        "name": "Dr. Hiroshi Nakamura",
        "email": "hiroshi@demo.com",
        "headline": "Neuroscience & Brain-Computer Interfaces",
        "bio": "Associate Professor of Neuroscience at Kyoto University. Researches brain-computer interfaces and neural prosthetics. Published 40+ papers on neural signal processing.",
        "rate": 210.0, "availability": "available",
        "domains": ["Medicine", "AI/ML"],
        "languages": [("English", "fluent"), ("Japanese", "native")],
        "competencies": [
            ("Kyoto University Faculty", "https://kyoto-u.ac.jp/example"),
            ("Science Magazine Publication", "https://science.org/example"),
            ("DARPA Grant Recipient", "https://darpa.mil/example"),
        ],
    },
    # 32
    {
        "name": "Amara Diallo",
        "email": "amara@demo.com",
        "headline": "Public Speaking & Leadership Coach",
        "bio": "Trained 500+ executives at Fortune 100 companies in public speaking and leadership presence. Former Toastmasters World Championship finalist. Author of two bestselling books.",
        "rate": 170.0, "availability": "available",
        "domains": ["Business", "Education"],
        "languages": [("English", "native"), ("French", "native"), ("Wolof", "native")],
        "competencies": [
            ("Published Author", "https://amazon.com/example"),
            ("Toastmasters Champion", "https://toastmasters.org/example"),
            ("LinkedIn Top Voice", "https://linkedin.com/example"),
        ],
    },
    # 33
    {
        "name": "Erik Lindqvist",
        "email": "erik@demo.com",
        "headline": "DevOps & Site Reliability Engineer",
        "bio": "Staff SRE at Spotify. Expert in Kubernetes, Terraform, CI/CD pipelines, and observability. Reduced downtime by 99.5% at three previous companies.",
        "rate": 165.0, "availability": "available",
        "domains": ["Engineering"],
        "languages": [("English", "fluent"), ("Swedish", "native")],
        "competencies": [
            ("CKA Certification", "https://cncf.io/example"),
            ("HashiCorp Ambassador", "https://hashicorp.com/example"),
            ("KubeCon Speaker", "https://kubecon.io/example"),
        ],
    },
    # 34
    {
        "name": "Dr. Camille Dubois",
        "email": "camille@demo.com",
        "headline": "Clinical Psychology Researcher",
        "bio": "Researcher at INSERM Paris studying anxiety disorders and PTSD. 12 years of clinical practice. Trains therapists in evidence-based trauma treatment protocols.",
        "rate": 160.0, "availability": "vacation",
        "domains": ["Medicine"],
        "languages": [("English", "fluent"), ("French", "native")],
        "competencies": [
            ("INSERM Research Profile", "https://inserm.fr/example"),
            ("APA Publication", "https://apa.org/example"),
        ],
    },
    # 35
    {
        "name": "Kwame Asante",
        "email": "kwame@demo.com",
        "headline": "Supply Chain & Operations Consultant",
        "bio": "Former McKinsey consultant. 10 years optimizing supply chains for manufacturing and retail companies. Reduced logistics costs by 30% for multiple clients.",
        "rate": 185.0, "availability": "available",
        "domains": ["Business"],
        "languages": [("English", "native"), ("Twi", "native"), ("French", "conversational")],
        "competencies": [
            ("McKinsey Alumni", "https://mckinsey.com/example"),
            ("APICS CSCP", "https://apics.org/example"),
            ("MIT SCM Certificate", "https://mit.edu/scm"),
        ],
    },
    # 36
    {
        "name": "Dr. Elena Moretti",
        "email": "elena@demo.com",
        "headline": "Astrophysics & Science Communication",
        "bio": "Postdoc at CERN. PhD in Particle Physics from Bologna University. Passionate science communicator with 200K YouTube subscribers explaining complex physics.",
        "rate": 75.0, "availability": "available",
        "domains": ["Science", "Education"],
        "languages": [("English", "fluent"), ("Italian", "native"), ("German", "conversational")],
        "competencies": [
            ("CERN Research Profile", "https://cern.ch/example"),
            ("YouTube Channel", "https://youtube.com/example"),
            ("Bologna PhD", "https://unibo.it/example"),
        ],
    },
    # 37
    {
        "name": "Rachel Nguyen",
        "email": "rachel@demo.com",
        "headline": "SEO & Growth Marketing Specialist",
        "bio": "Grew organic traffic from 0 to 5M monthly visits for three SaaS startups. Expert in technical SEO, content strategy, and conversion rate optimization.",
        "rate": 95.0, "availability": "available",
        "domains": ["Marketing"],
        "languages": [("English", "native"), ("Vietnamese", "fluent")],
        "competencies": [
            ("Google Search Central", "https://developers.google.com/search"),
            ("Moz Top 10 SEO", "https://moz.com/example"),
        ],
    },
    # 38
    {
        "name": "Dr. Arjun Mehta",
        "email": "arjun@demo.com",
        "headline": "AI Ethics & Responsible AI Consultant",
        "bio": "PhD in Computer Science from Carnegie Mellon. Leads responsible AI initiatives at a Big Tech company. Advises governments on AI regulation and fairness frameworks.",
        "rate": 200.0, "availability": "busy",
        "domains": ["AI/ML", "Law"],
        "languages": [("English", "native"), ("Hindi", "native"), ("Tamil", "conversational")],
        "competencies": [
            ("CMU PhD", "https://cmu.edu/example"),
            ("AAAI Fellow", "https://aaai.org/example"),
            ("EU AI Act Advisory", "https://ec.europa.eu/example"),
        ],
    },
    # 39
    {
        "name": "Sophie Laurent",
        "email": "sophie@demo.com",
        "headline": "Interior Design & Space Planning",
        "bio": "Award-winning interior designer featured in Architectural Digest. 10 years transforming residential and commercial spaces. Specializes in sustainable and biophilic design.",
        "rate": 105.0, "availability": "available",
        "domains": ["Design"],
        "languages": [("English", "fluent"), ("French", "native")],
        "competencies": [
            ("Architectural Digest Feature", "https://architecturaldigest.com/example"),
            ("NCIDQ Certified", "https://cidq.org/example"),
        ],
    },
    # 40
    {
        "name": "Tariq Mansoor",
        "email": "tariq@demo.com",
        "headline": "Tax Law & Compliance Expert",
        "bio": "15 years in international tax law. Advises multinational corporations on transfer pricing, tax treaties, and cross-border restructuring. Former Big Four tax partner.",
        "rate": 240.0, "availability": "available",
        "domains": ["Law", "Finance"],
        "languages": [("English", "fluent"), ("Arabic", "native"), ("Urdu", "fluent")],
        "competencies": [
            ("LLM in Taxation", "https://nyu.edu/example"),
            ("ADIT Qualification", "https://tax.org.uk/example"),
            ("Transfer Pricing Expert", "https://oecd.org/example"),
        ],
    },
    # 41
    {
        "name": "Yui Watanabe",
        "email": "yui@demo.com",
        "headline": "Mobile App Development Mentor",
        "bio": "Senior iOS engineer at a top ride-sharing company. 9 years building Swift and Kotlin apps. Open-source maintainer of a popular UI framework with 8K stars.",
        "rate": 90.0, "availability": "available",
        "domains": ["Engineering"],
        "languages": [("English", "fluent"), ("Japanese", "native")],
        "competencies": [
            ("App Store Featured", "https://apps.apple.com/example"),
            ("GitHub 8K Stars", "https://github.com/example"),
            ("WWDC Scholar", "https://developer.apple.com/wwdc"),
        ],
    },
    # 42
    {
        "name": "Dr. Nkem Eze",
        "email": "nkem@demo.com",
        "headline": "Public Health & Epidemiology Advisor",
        "bio": "MD and MPH from Johns Hopkins. 8 years in global health programs across Sub-Saharan Africa. Expert in infectious disease surveillance and health systems strengthening.",
        "rate": 150.0, "availability": "busy",
        "domains": ["Medicine"],
        "languages": [("English", "native"), ("Igbo", "native"), ("French", "basic")],
        "competencies": [
            ("Johns Hopkins MPH", "https://jhsph.edu/example"),
            ("CDC Consultant", "https://cdc.gov/example"),
        ],
    },
    # 43
    {
        "name": "Mateo Ruiz",
        "email": "mateo@demo.com",
        "headline": "Video Production & Storytelling Coach",
        "bio": "Emmy-nominated documentary filmmaker. 12 years producing branded content for tech companies. Teaches video production, scriptwriting, and motion graphics.",
        "rate": 85.0, "availability": "available",
        "domains": ["Marketing", "Design"],
        "languages": [("English", "native"), ("Spanish", "native")],
        "competencies": [
            ("Emmy Nomination", "https://emmys.com/example"),
            ("Vimeo Staff Pick", "https://vimeo.com/example"),
            ("LinkedIn Learning Instructor", "https://linkedin.com/learning"),
        ],
    },
    # 44
    {
        "name": "Dr. Ingrid Bergstrom",
        "email": "ingrid@demo.com",
        "headline": "NLP & Conversational AI Specialist",
        "bio": "PhD in Computational Linguistics from Uppsala University. Built dialogue systems for three major voice assistants. 25+ papers on transformer architectures and multilingual NLP.",
        "rate": 180.0, "availability": "vacation",
        "domains": ["AI/ML"],
        "languages": [("English", "fluent"), ("Swedish", "native"), ("German", "conversational")],
        "competencies": [
            ("Uppsala PhD", "https://uu.se/example"),
            ("ACL Best Paper Award", "https://aclweb.org/example"),
            ("Hugging Face Contributor", "https://huggingface.co/example"),
        ],
    },
]

# ── Chat Rooms (12) with 8-15 messages each ─────────────────────────
# Format: (client_idx, specialist_idx, [(sender_type, content), ...])
# sender_type: 0 = client, 1 = specialist
CHAT_DATA = [
    # Room 0: ML recommendation system (Alice + Dr. Sarah Chen)
    (0, 0, [
        (0, "Hi Dr. Chen! I need help with my ML project. We're building a recommendation system for e-commerce."),
        (1, "Great to hear from you! What kind of products are you working with, and how large is your dataset?"),
        (0, "Fashion items mainly. We have about 50K products and 2M users with browsing history."),
        (1, "Perfect scale for a hybrid approach. Have you tried any methods yet?"),
        (0, "We started with simple content-based filtering using product tags, but it's not performing well. CTR is around 2%."),
        (1, "That's a common starting point. Content-based alone misses the collaborative signal — what users with similar taste actually buy."),
        (0, "Exactly. We also noticed a cold-start problem with new products."),
        (1, "Let me outline a three-phase approach: first, we add collaborative filtering using implicit feedback. Then we build a hybrid model. Finally, we tackle cold-start with item embeddings."),
        (0, "That sounds comprehensive. How long would each phase take?"),
        (1, "Phase 1 is about 2 weeks if your data pipeline is clean. Phase 2 another 2 weeks. Phase 3 depends on your product taxonomy depth."),
        (0, "Our data pipeline needs some cleanup but it's mostly there. Can we start next Monday?"),
        (1, "Monday works. Let's schedule a 90-minute kickoff where I'll review your data schema and we can scope Phase 1 together."),
    ]),
    # Room 1: IP protection (Bob + Prof. James Miller)
    (1, 1, [
        (0, "Professor Miller, I need advice on protecting our startup's IP before we launch."),
        (1, "Happy to help! What type of IP are we talking about — patents, trademarks, trade secrets, or a combination?"),
        (0, "Mainly our software algorithm and brand name. We also have some proprietary training data."),
        (1, "Good that you're thinking about this early. For the algorithm, we should explore both patent and trade secret protection. For the brand, trademark registration is essential."),
        (0, "What's the difference between patenting the algorithm vs. keeping it as a trade secret?"),
        (1, "A patent gives you 20 years of protection but requires public disclosure. Trade secrets last indefinitely but you lose protection if someone reverse-engineers it independently."),
        (0, "Our algorithm is hard to reverse-engineer from the output. Trade secret might be better?"),
        (1, "That's often the right call for ML algorithms. We'll need NDAs for employees and contractors, and I'll help you set up proper documentation."),
        (0, "What about the training data? Can we protect that?"),
        (1, "Training data can be protected as a trade secret or through database rights in some jurisdictions. We should also review your data collection agreements."),
        (0, "Perfect. Can you draft a comprehensive IP strategy document for us?"),
        (1, "Absolutely. I'll prepare an IP audit and strategy memo. Should have a first draft by end of next week."),
    ]),
    # Room 2: UX audit (Carol + Lisa Thompson)
    (2, 4, [
        (0, "Hi Lisa! We need a UX audit for our mobile app. Our launch is in 3 weeks."),
        (1, "I can definitely help with that. Can you share the app or some screenshots to get started?"),
        (0, "I'll send you a TestFlight link. Main concern is the onboarding flow — we're losing 60% of users before they complete registration."),
        (1, "A 60% drop-off in onboarding is significant but not uncommon. Usually it means there are too many steps or the value proposition isn't clear early enough."),
        (0, "We have a 5-step onboarding: name, email, phone verification, preferences, tutorial."),
        (1, "That's quite a lot for initial onboarding. I'd recommend reducing it to 2 steps max: essential auth + one quick preference screen. Move the tutorial to contextual tooltips."),
        (0, "That makes sense. What about the phone verification? Our marketing team insists on it."),
        (1, "You could defer phone verification to when they take a key action, like making a purchase. That way you don't block exploration."),
        (0, "I love that idea. We also have some user feedback reports I can share."),
        (1, "Please do. I'll focus on onboarding, core navigation, and accessibility. I'll deliver a findings report with prioritized recommendations."),
        (0, "When can you start?"),
        (1, "I can start reviewing tomorrow. Expect the full audit report within 5 business days."),
    ]),
    # Room 3: Business English (Frank + Thomas Burke)
    (5, 13, [
        (0, "Hello Thomas! I want to improve my business English for presentations. I present quarterly results to international stakeholders."),
        (1, "Welcome Frank! What's your current level? Have you taken any proficiency tests?"),
        (0, "I'm around B2. I can communicate well in everyday situations but I struggle with formal presentations, especially during Q&A."),
        (1, "That's a great starting point. B2 to C1 for business contexts is very achievable. What specific challenges do you face during Q&A?"),
        (0, "I often can't find the right words quickly, and I sometimes get confused by idiomatic questions from native speakers."),
        (1, "Those are the two most common challenges. We'll work on: financial vocabulary, confident delivery techniques, and handling unexpected questions."),
        (0, "That's exactly what I need. How would you structure the sessions?"),
        (1, "I recommend twice-weekly 60-minute sessions. First month: vocabulary building and presentation structure. Second month: mock presentations with live Q&A practice."),
        (0, "Twice a week works for me. Can we schedule Tuesdays and Thursdays at 6 PM?"),
        (1, "Perfect. I'll prepare a diagnostic assessment for our first session so I can tailor the curriculum to your exact needs."),
        (0, "Sounds great. My next big presentation is in 8 weeks, so the timing is ideal."),
        (1, "We'll make sure you're well prepared. I'll send you some reading materials before our first session on Tuesday."),
        (0, "Thank you so much, Thomas!"),
    ]),
    # Room 4: React mentoring (Dave + Raj Patel)
    (3, 15, [
        (0, "Hi Raj, I'm transitioning from backend Java to full-stack and struggling with React state management."),
        (1, "Hey Dave! That's a common transition. Coming from Java, you'll find React's component model quite different from OOP patterns."),
        (0, "Exactly. I tried Redux but it felt overly complex with all the boilerplate. Someone recommended Zustand."),
        (1, "Zustand is a great choice. Think of it like a simplified singleton pattern — familiar from Java — but reactive. The API is minimal."),
        (0, "That analogy helps! I'm building a task management app to practice. What state should go in Zustand vs. component state?"),
        (1, "Good question. Rule of thumb: if two or more unrelated components need the same data, use Zustand. If it's local to one component tree, use useState or useReducer."),
        (0, "Makes sense. What about server state? I'm currently fetching data in useEffect and storing it in Zustand."),
        (1, "That's a common anti-pattern. For server state, use TanStack Query (React Query). It handles caching, refetching, loading states, and pagination out of the box."),
        (0, "So Zustand for client state and React Query for server state? That seems clean."),
        (1, "Exactly. That's the pattern we use at Netflix. Your Zustand store stays tiny — just auth state, UI preferences, maybe a shopping cart."),
        (0, "This is incredibly helpful. Can we do a pair-programming session where we refactor my app to use this pattern?"),
        (1, "Absolutely. Let's schedule a 2-hour session. Share your repo beforehand and I'll review the current architecture."),
        (0, "Sending you the GitHub link now. Available Saturday afternoon?"),
        (1, "Saturday 2 PM works. I'll come prepared with a migration plan for your app."),
    ]),
    # Room 5: Investment advice (Eve + Maria Garcia)
    (4, 2, [
        (0, "Hi Maria, I'm 35 and want to start planning seriously for retirement. I have about $50K in savings but no investment strategy."),
        (1, "Great that you're starting now — at 35 you have time on your side. First question: do you have an employer-sponsored 401(k)?"),
        (0, "Yes, my company matches up to 4% but I've only been contributing 2%."),
        (1, "Step one is easy: increase your 401(k) contribution to at least 4% to capture the full employer match. That's essentially free money."),
        (0, "I didn't realize how much I was leaving on the table. What about the $50K in savings?"),
        (1, "We should keep 3-6 months of expenses as an emergency fund in a high-yield savings account. The rest can be invested."),
        (0, "My monthly expenses are about $3,500. So maybe keep $15K as emergency fund?"),
        (1, "Exactly right. That leaves $35K to invest. Given your age and timeline, I'd recommend a diversified portfolio with 80% equities and 20% bonds."),
        (0, "Should I pick individual stocks or go with index funds?"),
        (1, "For most people, low-cost index funds are the best choice. Something like a total market index fund paired with an international fund gives you broad diversification with minimal fees."),
        (0, "That sounds manageable. Can you help me set up a concrete plan with specific fund allocations?"),
        (1, "Of course. Let me put together a detailed investment plan with specific fund recommendations and a contribution schedule. I'll have it ready by our next session."),
    ]),
    # Room 6: Marketing campaign (Grace + Carlos Rivera)
    (6, 11, [
        (0, "Hi Carlos! We're launching a B2B SaaS product in 6 weeks and need a comprehensive marketing strategy."),
        (1, "Exciting! Tell me about the product and your target audience."),
        (0, "It's a project management tool for remote teams. Target: 50-500 employee companies, primarily tech and creative agencies."),
        (1, "Good niche. What's your marketing budget for the launch, and do you have any existing audience?"),
        (0, "Budget is $15K for the launch quarter. We have a waitlist of 800 people and about 2K LinkedIn followers."),
        (1, "That's a solid starting point. With $15K, I'd allocate roughly 40% to LinkedIn ads (your audience lives there), 30% to content marketing, and 30% to a launch event."),
        (0, "We were thinking about Product Hunt as well. Is that worth the effort?"),
        (1, "Absolutely, but it needs careful preparation. I'd recommend aiming for a Tuesday or Wednesday launch, having 50+ supporters ready, and creating a compelling product video."),
        (0, "We don't have a video yet. Is that essential?"),
        (1, "For Product Hunt, yes. But a 60-second screen recording with voiceover is enough — no need for a polished commercial. I can guide you through creating one."),
        (0, "Perfect. What about our waitlist — how do we convert them?"),
        (1, "I'll design a drip email sequence: 3 emails leading up to launch, exclusive early access, and a referral incentive. We should aim for 30% waitlist-to-signup conversion."),
        (0, "Let's do it. Can you start with a detailed launch timeline?"),
        (1, "I'll have a week-by-week launch plan ready by Friday, covering content calendar, ad creative briefs, email sequences, and Product Hunt prep."),
    ]),
    # Room 7: Medical research (Henry + Dr. Yuki Tanaka)
    (7, 10, [
        (0, "Dr. Tanaka, I'm a medical resident working on a research paper about antibiotic resistance patterns in Southeast Asia."),
        (1, "That's a critically important topic. What stage are you at with the research?"),
        (0, "I've collected data from 3 hospitals over 2 years. About 12,000 culture results. I need help with the statistical analysis and methodology."),
        (1, "Impressive dataset. What's your primary research question — are you looking at temporal trends, geographic variation, or resistance mechanisms?"),
        (0, "Temporal trends mainly. I want to show how resistance patterns for specific pathogens have changed over the 2-year period."),
        (1, "For temporal trend analysis, I'd recommend using interrupted time series analysis or segmented regression. Have you worked with these methods before?"),
        (0, "I have basic stats knowledge — t-tests, chi-square. Nothing with time series."),
        (1, "No problem. I'll walk you through the methodology step by step. We'll use R for the analysis — it has excellent packages for epidemiological time series."),
        (0, "Which journal are you suggesting we target for publication?"),
        (1, "Given the scope and clinical relevance, I'd aim for the Journal of Antimicrobial Chemotherapy or Clinical Infectious Diseases. Both have good impact factors for this topic."),
        (0, "That would be amazing. Can we start with the methodology section?"),
        (1, "Let's schedule our first working session for this week. Please send me your dataset structure and any preliminary findings beforehand."),
    ]),
    # Room 8: Chemistry PhD help (Ivy + Dr. Mei Lin)
    (8, 18, [
        (0, "Dr. Lin, I'm a second-year PhD student in organic chemistry and I'm stuck on my synthesis pathway."),
        (1, "Tell me more about your target molecule and what approaches you've tried so far."),
        (0, "I'm trying to synthesize a novel indole derivative for potential antimalarial activity. My retrosynthesis looks good on paper but the key step keeps failing."),
        (1, "Which step is failing — is it the cyclization, a coupling reaction, or something else?"),
        (0, "It's a Suzuki coupling. I've tried different palladium catalysts, bases, and solvents but the yield is consistently below 10%."),
        (1, "Low yield in Suzuki coupling often points to problems with the boronic acid partner or the oxidative addition step. Are you using fresh boronic acid?"),
        (0, "It's been sitting on the shelf for about 6 months. Could that be the issue?"),
        (1, "Very likely. Boronic acids can protodeboronate over time, especially aryl ones. Try using the boronate ester instead, or get fresh reagent. Also, what's your reaction temperature?"),
        (0, "Room temperature with Pd(PPh3)4."),
        (1, "Try heating to 80C with Pd(dppf)Cl2 and K2CO3 in DMF/water. This catalyst system is much more robust for challenging substrates."),
        (0, "I'll try that combination this week. Can I share my TLC and NMR results with you?"),
        (1, "Please do. Send me the raw data and I'll help you interpret it. We can also discuss alternative routes if this doesn't work."),
    ]),
    # Room 9: Photography mentoring (Jack + Aisha Obi)
    (9, 24, [
        (0, "Hi Aisha! I'm an amateur photographer looking to improve my composition and lighting skills."),
        (1, "Welcome Jack! What kind of photography are you most interested in — portraits, landscape, street, or something else?"),
        (0, "Mostly street photography and urban landscapes. I have a mirrorless camera but I feel like my photos look flat."),
        (1, "Flat photos usually come down to two things: light quality and composition depth. When do you typically shoot?"),
        (0, "Mostly midday on weekends when I have free time."),
        (1, "That's your biggest issue right there. Midday light is harsh and creates unflattering shadows. Try shooting during golden hour — the first and last hour of sunlight."),
        (0, "I've heard of golden hour but never committed to it. What about composition?"),
        (1, "Beyond the rule of thirds, start looking for leading lines, frames within frames, and layers of foreground, midground, and background. These create depth."),
        (0, "Can you recommend some exercises to practice?"),
        (1, "Here's a week-long challenge: Day 1 — only leading lines. Day 2 — only reflections. Day 3 — only shadows. Day 4 — frame within a frame. This forces you to see differently."),
        (0, "I love that idea. Should I shoot in RAW or JPEG?"),
        (1, "Always RAW. It gives you much more latitude in post-processing. Speaking of which, do you edit your photos?"),
        (0, "I use the basic adjustments in Lightroom but I don't really know what I'm doing."),
        (1, "Let's add a post-processing module to our sessions. I'll show you how to bring out the mood and atmosphere of your street shots."),
    ]),
    # Room 10: Blockchain consulting (Kenji + Omar Farid)
    (10, 17, [
        (0, "Omar, our company is exploring blockchain for supply chain tracking. Can you advise on feasibility?"),
        (1, "Of course. Supply chain is one of the strongest use cases for blockchain. What industry are you in, and what problem are you trying to solve?"),
        (0, "Pharmaceutical distribution. We need to track drug provenance from manufacturer to pharmacy to comply with new EU regulations."),
        (1, "Pharma supply chain is perfect for blockchain. The EU Falsified Medicines Directive requires serialization and traceability. Are you looking at public or private blockchain?"),
        (0, "We're not sure. What would you recommend?"),
        (1, "For pharma, I'd recommend a permissioned blockchain like Hyperledger Fabric. It gives you the traceability without exposing sensitive business data on a public chain."),
        (0, "How long would a pilot project take?"),
        (1, "A proper pilot with 3-5 supply chain partners typically takes 3-4 months. That includes smart contract development, integration with your existing ERP, and testing."),
        (0, "What about costs? Our CTO wants a rough estimate."),
        (1, "For a pilot: roughly $80-120K including development, infrastructure, and consulting. Production rollout would be 3-5x that depending on scale."),
        (0, "That's within our budget for a pilot. Can you help us write a proposal for the board?"),
        (1, "Absolutely. I'll prepare a technical feasibility assessment with cost breakdown, timeline, and risk analysis. Should have it ready in 10 days."),
    ]),
    # Room 11: Fitness program (Luna + Viktor Novak)
    (11, 21, [
        (0, "Hi Viktor! I want to start a structured fitness program. I'm a complete beginner — haven't exercised regularly in years."),
        (1, "Welcome Luna! That's perfectly fine. Everyone starts somewhere. Can you tell me about your goals and any health considerations?"),
        (0, "I want to lose about 15kg and build some muscle. No major health issues, but I have mild lower back pain from sitting at a desk all day."),
        (1, "Good that you mentioned the back pain. We'll address that with core strengthening and mobility work. For your goals, we need a combination of resistance training and nutrition adjustments."),
        (0, "I'm a bit intimidated by weights. Can we start with bodyweight exercises?"),
        (1, "Absolutely. First 4 weeks will be bodyweight only: squats, push-ups progressions, planks, lunges, and rows using a resistance band. This builds a solid foundation."),
        (0, "How many days a week should I train?"),
        (1, "Let's start with 3 days: Monday, Wednesday, Friday. Each session about 45 minutes. Rest days are when your body actually gets stronger."),
        (0, "What about nutrition? I tend to skip breakfast and eat a big dinner."),
        (1, "That eating pattern makes it harder to lose fat. I'll create a meal plan that distributes protein evenly across 3-4 meals. You don't need to count calories obsessively, but protein timing matters."),
        (0, "How much protein do I need?"),
        (1, "Aim for about 1.6g per kg of your target body weight. So roughly 100-110g per day spread across your meals."),
        (0, "This all sounds doable. When can we start?"),
        (1, "Let's start Monday. I'll send you a Week 1 workout plan and a grocery list for meal prep this weekend."),
        (0, "Thank you, Viktor! I'm excited to get started."),
        (1, "You've got this. Consistency beats intensity every time. Let's check in after the first week and adjust from there."),
    ]),
]

# ── Reviews (35) ─────────────────────────────────────────────────────
# Format: (specialist_idx, client_idx, rating, comment)
REVIEW_DATA = [
    # Dr. Sarah Chen (idx 0)
    (0, 0, 5, "Dr. Chen is incredibly knowledgeable about ML. Helped me solve a complex NLP problem in just 2 sessions."),
    (0, 1, 5, "Best AI consultant I've worked with. Clear explanations and practical advice that we could implement immediately."),
    (0, 2, 4, "Very helpful but sometimes hard to schedule due to high demand. When you do get time with her, it's excellent."),
    # Prof. James Miller (idx 1)
    (1, 0, 5, "Prof. Miller saved us thousands in legal fees with his expert guidance on our IP strategy."),
    (1, 3, 5, "Outstanding legal advice. Thorough, professional, and always available for follow-up questions."),
    (1, 10, 4, "Excellent knowledge but his rates are on the higher end. Worth it for complex matters though."),
    # Lisa Thompson (idx 4)
    (4, 2, 5, "Lisa completely transformed our app's UX. User satisfaction went up 40% after implementing her recommendations."),
    (4, 4, 4, "Great designer but wished for faster turnaround on deliverables."),
    (4, 11, 5, "Incredible eye for detail. She found usability issues our entire team had missed."),
    # Michael Chang (idx 7)
    (7, 1, 5, "Michael's startup advice is worth every penny. Our revenue doubled after his strategic guidance."),
    (7, 3, 5, "Incredible mentor. His network alone was worth the investment."),
    (7, 12, 3, "Very smart but his advice is geared toward VC-backed startups. Less relevant for bootstrapped businesses."),
    # Thomas Burke (idx 13)
    (13, 5, 5, "Thomas made my presentations so much better. Got promoted partly thanks to his coaching!"),
    (13, 6, 5, "Patient, professional, and genuinely fun to work with. Highly recommend for business English."),
    (13, 7, 4, "Good teacher but I wish sessions were longer. 60 minutes goes by fast."),
    (13, 14, 3, "Decent for general business English but I needed more specialized financial vocabulary."),
    # Raj Patel (idx 15)
    (15, 3, 5, "Raj explains complex React concepts so clearly. Best coding mentor I've ever had."),
    (15, 8, 4, "Very knowledgeable but sometimes moves a bit too fast for beginners."),
    (15, 13, 5, "Helped me land a senior frontend role. His mock interviews were incredibly realistic."),
    # Viktor Novak (idx 21)
    (21, 9, 5, "Viktor's fitness program changed my life. Down 20kg in 6 months! Science-based and sustainable."),
    (21, 11, 5, "Finally a coach who doesn't push fad diets. Evidence-based nutrition and realistic goals."),
    (21, 15, 4, "Great program but I wish there was more flexibility in scheduling sessions."),
    # Carlos Rivera (idx 11)
    (11, 6, 4, "Solid marketing strategy that drove real results. Our MQLs increased by 65%."),
    (11, 16, 2, "Felt like the advice was too generic. Expected more customized strategy for our niche."),
    # Dr. Yuki Tanaka (idx 10)
    (10, 7, 5, "Dr. Tanaka's guidance on our clinical trial design was invaluable. Saved us months of potential missteps."),
    (10, 14, 4, "Excellent researcher. Very thorough in her methodology review."),
    # Maria Garcia (idx 2)
    (2, 4, 4, "Maria helped me create a solid retirement plan. Clear explanations of complex financial concepts."),
    (2, 17, 3, "Good general advice but I expected more advanced strategies for my income level."),
    # Ahmed Hassan (idx 5)
    (5, 12, 5, "Ahmed found critical vulnerabilities in our infrastructure that our internal team missed completely."),
    (5, 10, 1, "Scheduled a session but he had to reschedule twice. When we finally met, the session was rushed."),
    # Sofia Rossi (idx 8)
    (8, 8, 5, "Sofia helped me structure my entire PhD thesis. Her feedback on academic writing was transformative."),
    # Dr. Anna Petrov (idx 12)
    (12, 13, 3, "Knowledgeable but often unavailable due to being marked as busy. Hard to schedule follow-ups."),
    # Omar Farid (idx 17)
    (17, 10, 4, "Deep knowledge of DeFi protocols. Helped us avoid several costly smart contract pitfalls."),
    # Priya Sharma (idx 22)
    (22, 16, 2, "The visualizations were nice but she missed the project deadline by a week without communication."),
    # Dr. Laura Santos (idx 16)
    (16, 0, 5, "Dr. Santos helped me develop my leadership skills through a structured coaching program. Life-changing."),
]

# ── Task Requests (18) ───────────────────────────────────────────────
# Format: (client_idx, domain, urgency, comment, budget_min, budget_max, status)
TASK_REQUESTS_DATA = [
    (0, "AI/ML", "high",
     "Need help building a recommendation system for my e-commerce platform. We have 50K products and 2M users with browsing history.",
     100, 200, "open"),
    (1, "Law", "medium",
     "Looking for guidance on intellectual property protection for our SaaS startup before launching.",
     150, 300, "open"),
    (2, "Finance", "low",
     "Would like advice on investment portfolio diversification for retirement. Currently 35 with $50K in savings.",
     80, 150, "in_progress"),
    (3, "Design", "urgent",
     "Need a UX audit for our mobile app before launch next week. Currently losing 60% of users during onboarding.",
     70, 120, "open"),
    (4, "Engineering", "medium",
     "Looking for a cloud architect to design our AWS infrastructure for a microservices migration.",
     None, None, "open"),
    (5, "Education", "low",
     "I need a business English tutor for presentation skills. B2 level, weekly sessions preferred.",
     30, 60, "in_progress"),
    (6, "Marketing", "high",
     "Need a digital marketing strategist for our B2B SaaS product launch campaign. $15K budget for the quarter.",
     100, 180, "open"),
    (7, "Science", "medium",
     "PhD student looking for guidance on organic chemistry research methodology and statistical analysis.",
     None, None, "open"),
    (8, "Other", "low",
     "Looking for a photography mentor to improve my composition and lighting skills for street photography.",
     40, 80, "in_progress"),
    (9, "Other", "medium",
     "Need a fitness coach for a structured 3-month training program with nutrition plan. Complete beginner.",
     30, 70, "open"),
    (10, "AI/ML", "high",
     "Need an AI ethics consultant to review our facial recognition system for bias before deployment.",
     150, 250, "open"),
    (11, "Medicine", "urgent",
     "Looking for a biostatistics expert to help with statistical analysis for a clinical trial paper. Deadline in 3 weeks.",
     120, 220, "in_progress"),
    (12, "Business", "medium",
     "Early-stage startup seeking a strategy coach for fundraising preparation. Series A target of $5M.",
     200, 350, "open"),
    (13, "Engineering", "high",
     "Need a DevOps consultant to set up CI/CD pipelines and Kubernetes infrastructure for our growing team.",
     130, 200, "open"),
    (14, "Marketing", "low",
     "Looking for an SEO specialist to audit our website and develop a 6-month organic growth strategy.",
     70, 120, "closed"),
    (15, "Law", "urgent",
     "Need urgent advice on international tax compliance for our expansion into the EU market.",
     200, 300, "in_progress"),
    (16, "Design", "medium",
     "Looking for an interior designer to redesign our 200sqm co-working office space with biophilic design elements.",
     80, 130, "closed"),
    (17, "Education", "low",
     "Want to learn German for business purposes. Currently A2 level, targeting B2 within a year.",
     40, 70, "closed"),
]

# ── Proposals (18) ───────────────────────────────────────────────────
# Format: (task_request_idx, specialist_idx, message, price_offer)
PROPOSALS_DATA = [
    (0, 0, "I can help you build a hybrid recommendation system combining collaborative filtering and content-based approaches. I've built similar systems for Amazon-scale platforms.", 140.0),
    (0, 3, "I specialize in recommendation engines and have extensive experience with e-commerce data at this scale. Let's start with a data audit.", 95.0),
    (1, 1, "IP protection for SaaS is my specialty. I'll create a comprehensive strategy covering patents, trademarks, and trade secrets.", 230.0),
    (1, 26, "I've handled IP strategies for dozens of tech startups. Happy to provide a thorough IP audit and protection plan.", 260.0),
    (3, 4, "I'd love to help with your UX audit. I'll use my Apple design methodology to identify key onboarding improvements.", 85.0),
    (4, 9, "I can design a scalable AWS architecture for your microservices. I've done similar migrations for enterprise clients.", 170.0),
    (4, 33, "Kubernetes-based microservices architecture is my specialty. I'll set up your infrastructure with proper CI/CD from day one.", 160.0),
    (5, 13, "I'd be happy to help with business English presentations. I have a proven curriculum for B2 speakers targeting C1.", 45.0),
    (6, 11, "I'll create a comprehensive launch strategy including LinkedIn ads, content calendar, Product Hunt prep, and email sequences.", 125.0),
    (6, 28, "Brand strategy and launch campaigns are my forte. I've launched 30+ products and know what drives B2B SaaS adoption.", 140.0),
    (8, 24, "As a published photographer, I can help you master composition and lighting through hands-on projects and weekly challenges.", 60.0),
    (9, 21, "I'll create a personalized 3-month program combining bodyweight training, progressive overload, and evidence-based nutrition planning.", 50.0),
    (10, 38, "AI ethics and bias auditing is exactly my specialization. I've reviewed facial recognition systems for both companies and government agencies.", 195.0),
    (11, 25, "I can provide comprehensive biostatistical support for your clinical trial paper, including study design review and analysis.", 185.0),
    (12, 7, "I've helped 20+ startups through their Series A. Let me review your pitch deck and fundraising strategy.", 280.0),
    (13, 33, "I'll design and implement your complete CI/CD and Kubernetes setup. Includes monitoring, alerting, and disaster recovery.", 160.0),
    (14, 37, "I'll conduct a thorough SEO audit and build a data-driven content strategy targeting your highest-value keywords.", 90.0),
    (15, 40, "International tax compliance for EU expansion is exactly what I do. I can help with transfer pricing and VAT registration.", 235.0),
]


# ══════════════════════════════════════════════════════════════════════
# SEED FUNCTION
# ══════════════════════════════════════════════════════════════════════

async def seed(reset: bool = False) -> None:
    import subprocess
    backend_dir = str(Path(__file__).resolve().parent.parent)

    if reset:
        # Drop everything and recreate schema
        async with async_session() as db:
            print("Dropping all tables...")
            await db.execute(text("DROP SCHEMA public CASCADE"))
            await db.execute(text("CREATE SCHEMA public"))
            await db.commit()
            print("Schema recreated.")

    # Apply migrations (creates all tables)
    print("Applying migrations...")
    subprocess.run(["alembic", "upgrade", "head"], cwd=backend_dir, check=True)
    print("Migrations applied.")

    async with async_session() as db:
        # ── Check if data already exists ─────────────────────────────
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        if result.scalar() > 0:
            print("Database already seeded. Use --reset to truncate and re-seed.")
            return

        # ── Clients ──────────────────────────────────────────────────
        clients = []
        for name, email in CLIENTS_DATA:
            user = User(
                email=email,
                password_hash=PASSWORD,
                role=UserRole.CLIENT,
                full_name=name,
            )
            db.add(user)
            clients.append(user)

        # ── Specialist users ─────────────────────────────────────────
        specialist_users = []
        for spec in SPECIALISTS_DATA:
            user = User(
                email=spec["email"],
                password_hash=PASSWORD,
                role=UserRole.SPECIALIST,
                full_name=spec["name"],
            )
            db.add(user)
            specialist_users.append(user)

        await db.flush()

        # ── Specialist profiles + domains + languages + competencies ─
        profiles = []
        for i, spec in enumerate(SPECIALISTS_DATA):
            profile = SpecialistProfile(
                user_id=specialist_users[i].id,
                headline=spec["headline"],
                bio=spec["bio"],
                hourly_rate=spec["rate"],
                availability=AVAIL[spec["availability"]],
                avg_rating=0.0,
                review_count=0,
            )
            db.add(profile)
            profiles.append(profile)

        await db.flush()

        for i, spec in enumerate(SPECIALISTS_DATA):
            for domain in spec["domains"]:
                db.add(SpecialistDomain(specialist_id=profiles[i].id, domain=domain))
            for lang, prof in spec["languages"]:
                db.add(SpecialistLanguage(
                    specialist_id=profiles[i].id,
                    language=lang,
                    proficiency=LanguageProficiency(prof),
                ))
            for j, (label, url) in enumerate(spec["competencies"]):
                db.add(SpecialistCompetency(
                    specialist_id=profiles[i].id,
                    label=label,
                    url=url,
                    display_order=j,
                ))

        # ── Chat rooms + messages ────────────────────────────────────
        rooms = []
        for client_idx, spec_idx, messages_list in CHAT_DATA:
            room = ChatRoom(
                client_id=clients[client_idx].id,
                specialist_id=specialist_users[spec_idx].id,
            )
            db.add(room)
            await db.flush()
            rooms.append(room)

            for sender_type, content in messages_list:
                sender_id = (
                    clients[client_idx].id if sender_type == 0
                    else specialist_users[spec_idx].id
                )
                db.add(Message(room_id=room.id, sender_id=sender_id, content=content))

        # ── Reviews ──────────────────────────────────────────────────
        for spec_idx, client_idx, rating, comment in REVIEW_DATA:
            db.add(Review(
                specialist_id=profiles[spec_idx].id,
                client_id=clients[client_idx].id,
                rating=rating,
                comment=comment,
            ))

        await db.flush()

        # ── Recalculate avg_rating and review_count ──────────────────
        for profile in profiles:
            result = await db.execute(
                select(
                    sqlfunc.count(Review.id),
                    sqlfunc.coalesce(sqlfunc.avg(Review.rating), 0),
                ).where(Review.specialist_id == profile.id)
            )
            count, avg = result.one()
            profile.avg_rating = round(float(avg), 1) if count > 0 else 0.0
            profile.review_count = count

        # ── Task requests ────────────────────────────────────────────
        urgency_map = {
            "low": Urgency.LOW,
            "medium": Urgency.MEDIUM,
            "high": Urgency.HIGH,
            "urgent": Urgency.URGENT,
        }
        status_map = {
            "open": RequestStatus.OPEN,
            "in_progress": RequestStatus.IN_PROGRESS,
            "closed": RequestStatus.CLOSED,
        }

        task_requests = []
        for client_idx, domain, urgency, comment, budget_min, budget_max, status in TASK_REQUESTS_DATA:
            tr = TaskRequest(
                client_id=clients[client_idx].id,
                domain=domain,
                urgency=urgency_map[urgency],
                comment=comment,
                budget_min=budget_min,
                budget_max=budget_max,
                status=status_map[status],
            )
            db.add(tr)
            task_requests.append(tr)

        await db.flush()

        # ── Proposals ────────────────────────────────────────────────
        for req_idx, spec_idx, message, price in PROPOSALS_DATA:
            db.add(TaskProposal(
                request_id=task_requests[req_idx].id,
                specialist_id=specialist_users[spec_idx].id,
                message=message,
                price_offer=price,
            ))

        # ── Commit ───────────────────────────────────────────────────
        await db.commit()

        print("Seed data created successfully!")
        print(f"  Created: {len(clients)} clients, {len(specialist_users)} specialists")
        print(f"  Created: {len(rooms)} chat rooms, {len(REVIEW_DATA)} reviews")
        print(f"  Created: {len(task_requests)} task requests, {len(PROPOSALS_DATA)} proposals")
        print()
        print("Demo accounts:")
        print("  Client:     client@demo.com / Demo1234!")
        print("  Specialist: expert@demo.com / Demo1234!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed demo data for Bridge")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Truncate all tables before seeding",
    )
    args = parser.parse_args()
    asyncio.run(seed(reset=args.reset))
