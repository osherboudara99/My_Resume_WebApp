// Single source of truth for the site's static content. Anything the AI Twin
// needs to know lives in the backend corpus, not here.

export const NAME = 'Osher Boudara'
export const TWIN_NAME = "Osher's AI Twin"
export const GITHUB_USERNAME = 'osherboudara99'

// Apple has no API for lifetime play count, so this is captured manually by
// summing Music.app's per-track "played count" (see scripts/apple-music-plays.sh)
// and re-run occasionally. `musicStats.ts` grows this number forward from
// APPLE_MUSIC_BASE_DATE with a small deterministic daily drift so the stat
// still feels alive between refreshes instead of going stale.
export const APPLE_MUSIC_TOTAL_PLAYS = 71044
export const APPLE_MUSIC_BASE_DATE = '2026-07-26'

export const TITLES = [
  'an Applied AI Engineer.',
  'a Full Stack Developer.',
  'a Data Scientist.',
  'a Python Developer.',
  'a Solutions Architect.',
  'a Musician.',
  'a Data Engineer.',
  'a Software Engineer.',
  'a Machine Learning Engineer.',
]

export const SOCIALS = {
  linkedin: 'https://www.linkedin.com/in/osher-boudara-a612921b5/',
  github: 'https://www.github.com/osherboudara99/',
  linkedinCertifications:
    'https://www.linkedin.com/in/osher-boudara-a612921b5/details/certifications/',
}

export const BIO = [
  "I'm a Senior Data Scientist at Cognizant, leading data science initiatives for a Fortune 500 Crop Science client. I partner closely with stakeholders to design, develop, and deploy scalable machine learning and generative AI solutions that drive measurable business impact.",
  'My work spans statistical modeling, machine learning, generative AI, and cloud-based architectures. I specialize in transforming complex datasets into actionable insights and building production-ready systems that create lasting value.',
  'I earned a B.S. in Computer Science with a minor in Statistics from California State University, Northridge, graduating with honors. Based in Los Angeles and bilingual, I enjoy producing and playing music, training, exploring new cuisines, and traveling — and I’m a proud Los Angeles Rams fan.',
]

export interface Certification {
  file: string
  name: string
  issuer: string
  credentialUrl?: string
}

export const CERTIFICATIONS: Certification[] = [
  {
    file: '/certifications/Osher_B_AWS_SA_cert.pdf',
    name: 'AWS Certified Solutions Architect – Associate',
    issuer: 'Amazon Web Services',
    credentialUrl: 'https://www.credly.com/badges/cb536cd2-586f-411f-b1e9-915d8980103d',
  },
  {
    file: '/certifications/Osher_B_ml_specialization_UW_Coursera_cert.pdf',
    name: 'Machine Learning Specialization',
    issuer: 'University of Washington — Coursera',
    credentialUrl:
      'https://www.coursera.org/account/accomplishments/specialization/ADDB2SJ6MNF3',
  },
  {
    file: '/certifications/Osher_B_AZ900_cert_rotated.pdf',
    name: 'Microsoft Certified: Azure Fundamentals (AZ-900)',
    issuer: 'Microsoft',
    credentialUrl:
      'https://learn.microsoft.com/en-us/users/osherboudara-7874/credentials/3e3599c5dccdd406',
  },
  {
    file: '/certifications/Osher_B_Database_Tech_USDL_cert.pdf',
    name: 'Database Technician Apprenticeship',
    issuer: 'U.S. Department of Labor',
  },
]

export const SECTIONS = [
  { id: 'about', label: 'About' },
  { id: 'projects', label: 'Projects' },
  { id: 'resume', label: 'Resume' },
  { id: 'certifications', label: 'Certifications' },
] as const
