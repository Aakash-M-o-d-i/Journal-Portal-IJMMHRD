# IJMMHRD — Product Requirements Document (PRD)

**International Journal of Multidisciplinary Modern Research and Development**

## 1. Product Overview

IJMMHRD is a clean, simple academic journal publishing and digital library platform. It supports public article discovery, manuscript submission, peer review, revision, editorial decisions, publication, and DOI management.

The product should prioritize **ease of use over feature complexity**.

**Primary product flow:**

> Find Article → Submit Paper → Track Paper → Review → Revise → Accept → Publish → DOI

## 2. Product Goals

- Provide a professional, easy-to-navigate academic journal website.
- Make manuscript submission and tracking straightforward for authors.
- Give administrators/editors a simple internal workflow for managing peer reviews.
- Give editors one simple place to manage submissions, reviewers, publication, and content.
- Automatically generate a DOI-style identifier when an article is ready for publication.
- Clearly separate internal DOI generation from official DOI registration.
- Provide searchable archives and article pages with PDF access.

## 3. Technology Stack & Deployment

The application will use a simple Python-based backend suitable for the current cPanel hosting environment.

| Component | Technology |
|---|---|
| Backend | Python 3.x + Flask |
| Frontend | HTML5 + CSS3 + JavaScript |
| Database | MySQL |
| Database Access | Python MySQL driver / SQLAlchemy as needed |
| Web Hosting | cPanel / Apache with **Setup Python App** |
| File Storage | Server-side uploads directory |
| Authentication | Flask session-based authentication with secure password hashing |

The hosting environment has been verified to provide **Setup Python App**, **Python Packages**, **MySQL Databases**, **phpMyAdmin**, and **Terminal**, so the deployment should be designed for this environment.

## 4. Target Users

| User | Main Need |
|---|---|
| Public / Reader | Discover, search, read and download published research. |
| Author | Submit papers, track progress, upload revisions and see decisions. |
| Admin / Editor | Manage submissions, reviews, publication, DOI data, users and website content. |

## 5. Product Scope

### 5.1 Public Website

- Home
- About
- Editorial Board
- Author Guidelines
- Submit Paper
- Track Paper
- Archives
- Search Articles
- Article Details + PDF
- Contact

### 5.2 Author Area

Keep this as **one simple author application/dashboard**.

- Dashboard
- Submit Paper
- My Papers
- Paper Details
- Track Status
- Upload Revision
- View Decision
- View Publication
- View DOI
- Edit own profile/contact details

The author should not need to understand or access reviewer/editor administration functions.

### 5.3 Admin / Editor Area

A single protected administration area is used internally.

- Dashboard
- Submissions
- Review Management
- Decisions
- Articles
- DOI Management
- Volumes & Issues
- Editorial Board
- Users
- **Website Content Management**

### 5.4 Website Content Management (No Developer Required)

Authorized Admin/Editor users must be able to update normal website content directly from the Admin area without changing source code.

Editable content should include:

- Home page text and sections
- About / Aim & Scope
- Author Guidelines
- Publication / Processing Charges
- Editorial Board
- Contact information
- Announcements / News
- Call for Papers
- Important links
- Footer text
- Journal metadata such as ISSN, email and publication frequency

The content management interface should use simple forms/editors with **Save, Preview and Publish** actions.

Changes should appear on the public website after publishing. The developer should only be required for new functionality or structural changes, not routine content updates.

## 6. Core Publishing Workflow

1. Author submits manuscript and author/co-author information.
2. Admin/Editor performs an initial suitability check.
3. Admin/Editor assigns reviewer(s) internally.
4. Reviewer activity is managed internally by the Admin/Editor area; a separate reviewer-facing application is not required for the initial version.
5. Admin/Editor records the review outcome and decides: Accept, Minor Revision, Major Revision, or Reject.
6. If revision is required, author uploads a revised manuscript and response.
7. Admin/Editor completes the final decision.
8. Accepted manuscript is prepared as a published article and assigned to a volume/issue.
9. System generates a DOI identifier and displays it on the article page.
10. Official DOI registration remains a separate external registration step.

**Design principle:** Do not build separate Author, Reviewer and Admin applications. Build one website with a simple Author area and one protected Admin/Editor area.

## 7. DOI Product Requirement

The system must provide a simple **DOI Management** area.

- Generate a unique DOI-style identifier automatically for a publishable article.
- Store DOI against the article record.
- Show DOI on the public article page.
- Allow admin/editor to copy the DOI and DOI URL.
- Track DOI status: `Pending / Generated / Registered`.
- Do not label an internally generated identifier as officially registered until registration succeeds with a DOI registration agency.

### Suggested DOI format

```text
10.xxxx/ijmmhrd.2026.001
```

The exact DOI prefix must be configurable rather than hard-coded.

## 8. IJIRT-Inspired Information Architecture & UI/UX

The public website should be **inspired by the information architecture and usability patterns of IJIRT**, while using original IJMMHRD branding, copy, graphics and visual styling. Do not make a pixel-for-pixel copy.

### 8.1 Header / Main Navigation

Use a simple academic-journal header with:

- IJMMHRD logo / journal name
- Authors menu
  - Paper Format
  - Submit Paper
  - Track Paper
  - Author Guidelines
  - How to Publish
  - Processing Charges
- Research Areas
- Archive
- About
- Contact
- Clear **Submit Paper** primary button
- **Author Login** link

### 8.2 Homepage Layout

Use a simple content hierarchy similar to the reference journal:

1. Journal identity / hero area
2. Short journal introduction
3. Primary actions: **Submit Paper** and **Track Paper**
4. Journal statistics / key information
5. Search published papers
6. Latest publications
7. Research areas
8. Current issue / archive
9. How to publish
10. Submission call-to-action
11. Footer with important links and policies

The homepage should be information-rich but visually uncluttered.

### 8.3 Publication Search

Provide a prominent journal search area supporting:

- Paper ID
- Published Article ID
- Paper Title
- Author Name
- Keywords / research area

Search results should show:

- Article title
- Authors
- Year
- Volume
- Issue
- Page numbers
- Article details
- PDF
- DOI

### 8.4 Archive Structure

Use a simple archive hierarchy:

```text
Year
  ↓
Volume
  ↓
Issue
  ↓
Published Articles
```

Each article listing should provide its metadata and a clear link to the article page/PDF.

### 8.5 Author Experience

Use a simple Paper ID + Email based author access option, inspired by IJIRT, so authors do not need a complicated account system for the initial version.

Author flow:

```text
Submit Paper
    ↓
Paper ID Generated
    ↓
Confirmation
    ↓
Paper ID + Email
    ↓
Author Area
    ↓
Track / Revise / View Decision / Publication / DOI
```

If full password accounts are implemented later, Paper ID tracking should remain available as a convenient option.

### 8.6 Article Page

Each published article should have a clean scholarly article page containing:

- Article title
- Author names
- Affiliations
- Abstract
- Keywords
- Publication date
- Volume / Issue
- Page numbers
- Paper / Article ID
- DOI
- Citation information
- Download PDF
- BibTeX / citation export

### 8.7 Admin Content Editing

The Admin/Editor area must include a simple CMS so authorized staff can maintain the website without a developer.

Routine content must be editable through forms/editor screens:

- Homepage sections
- Research areas
- About / Aim & Scope
- Author Guidelines
- Paper Format information
- How to Publish
- Processing Charges
- Editorial Board
- Policies
- News / Announcements
- Call for Papers
- Contact details
- Footer links
- Journal metadata

Use:

`Edit → Preview → Save Draft → Publish → Unpublish`

## 9. UI/UX Principles

The UI/UX should take inspiration from clean academic journal portals such as IJIRT while remaining simpler.

- Clean academic look.
- Simple navigation.
- Clear primary actions.
- Responsive desktop and mobile layouts.
- Cards, tables, badges, breadcrumbs and clear status indicators.
- Avoid unnecessary sliders.
- Avoid heavy glassmorphism.
- Avoid complex dashboards.
- Avoid excessive animations.
- Keep common tasks to as few steps as practical.

## 10. Out of Scope for Initial Version

- Advanced full-text PDF indexing/search.
- Complex business intelligence analytics.
- Multiple complicated document formats unless required.
- Large CMS/editorial automation beyond essential publishing content.
- Automatic official DOI registration unless a registration-agency integration is implemented.

## 11. Success Criteria

- A reader can find an article quickly.
- An author can submit and track a paper without assistance.
- A reviewer can complete a review from one focused workspace.
- An editor can move a paper from submission through publication without manual database work.
- A published article has clear metadata, PDF access, and DOI information.
