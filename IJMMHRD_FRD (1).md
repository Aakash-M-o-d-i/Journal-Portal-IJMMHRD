# IJMMHRD — Functional Requirement Document (FRD)

**International Journal of Multidisciplinary Modern Research and Development**

## 1. System Actors

| Actor | Access |
|---|---|
| Guest / Public | Public journal pages, article search, archives, PDFs, submission entry. |
| Author | Own submissions, revisions, decisions, publication details and own profile. |
| Admin / Editor | Full editorial workflow, reviewer management, users, content, articles, issues and DOI management. |

## 2. Technology & Deployment Requirements

- Backend must use **Python 3.x with Flask**.
- Frontend must use **HTML5, CSS3 and JavaScript**.
- Database must use **MySQL**.
- Application must be deployable using the hosting provider's **cPanel → Setup Python App** feature.
- Python dependencies must be installable through the available **Python Packages / pip** environment.
- Database administration should remain compatible with **MySQL / phpMyAdmin**.
- Keep the architecture simple and avoid unnecessary external services for the initial version.
- Use one application with role-based access rather than separate Author, Reviewer and Admin applications.

## 3. IJIRT-Inspired UI/UX Functional Requirements

The implementation should follow the reference journal's **information architecture and workflow patterns**, but must use original IJMMHRD branding and content.

### FR-UI-01 Main Navigation

Provide a simple navigation structure for Authors, Research Areas, Archive, About and Contact, with prominent Submit Paper and Author Login actions.

### FR-UI-02 Author Menu

The Authors section should expose:

- Paper Format
- Submit Paper
- Track Paper
- Author Guidelines
- How to Publish
- Processing Charges

### FR-UI-03 Homepage

The homepage must present:

- Journal identity
- Short introduction
- Submit Paper CTA
- Track Paper CTA
- Published-paper search
- Latest publications
- Research areas
- Current issue / archives
- Publishing workflow
- Important policies and footer links

### FR-UI-04 Publication Search

Search must support Paper ID, published article ID, paper title, author name and keywords/research area.

### FR-UI-05 Archive

Users must be able to navigate:

`Year → Volume → Issue → Articles`

### FR-UI-06 Author Access

Provide simple author access using **Paper ID + Email**. The system generates a unique Paper ID after successful submission.

### FR-UI-07 Article Details

Published article pages must display article metadata, abstract, authors, affiliations, volume, issue, pages, article ID, DOI, PDF link and citation/BibTeX options.

### FR-UI-08 Responsive Layout

Public pages and author/admin screens must work on desktop, tablet and mobile.

### FR-UI-09 Content Management

Authorized Admin/Editor users must be able to update routine website content without developer involvement.

Editable areas must include homepage sections, research areas, About/Aim & Scope, guidelines, paper format information, publishing instructions, charges, editorial board, policies, announcements, calls for papers, contact information, footer links and journal metadata.

Each content item should support:

`Edit → Preview → Save Draft → Publish → Unpublish`

### FR-UI-10 Original Design

The application may be inspired by IJIRT's information architecture and user flows but must not copy its logo, text, images, branding or pixel-level visual design.

## 4. Public Website Requirements

| ID | Feature | Functional Requirement |
|---|---|---|
| FR-PUB-01 | Home | Display journal identity, key information, latest publications and important links. |
| FR-PUB-02 | Article Search | Search article title, abstract, keywords and author names. |
| FR-PUB-03 | Archives | Browse publications by volume, issue and year. |
| FR-PUB-04 | Article Page | Display title, abstract, keywords, authors, affiliations, DOI and PDF access. |
| FR-PUB-05 | Submission | Provide manuscript submission form with co-author information and manuscript upload. |
| FR-PUB-06 | Track Paper | Allow an author to identify a submission and view its current status. |
| FR-PUB-07 | Static Content | Display About, Guidelines, Editorial Board, Charges and Contact information. |

## 5. Author Requirements

| ID | Feature | Functional Requirement |
|---|---|---|
| FR-AUTH-01 | Dashboard | Show the author's submitted manuscripts and current status. |
| FR-AUTH-02 | Submit Paper | Allow the author to submit a manuscript with paper details and co-author information. |
| FR-AUTH-03 | Submission Details | Show title, submission code, status and relevant editorial decision information. |
| FR-AUTH-04 | Revision | Allow an author to upload a revised manuscript and response when revision is requested. |
| FR-AUTH-05 | Decision | Show the editorial decision after it is recorded. |
| FR-AUTH-06 | Publication | Show publication details, volume/issue, article page and DOI when published. |
| FR-AUTH-07 | Profile | Allow the author to update their own basic profile/contact information. |

## 6. Review Management Requirements

Reviewers are managed **internally by the Admin/Editor area** in the initial version. A separate reviewer-facing portal/application is not required.

| ID | Feature | Functional Requirement |
|---|---|---|
| FR-REV-01 | Reviewer Records | Admin can create and manage reviewer records. |
| FR-REV-02 | Assignment | Admin can assign a reviewer to a manuscript and set a due date. |
| FR-REV-03 | Review Entry | Admin can record/import the review outcome, rating, recommendation and comments. |
| FR-REV-04 | Review Status | Admin can track pending, received and overdue reviews. |
| FR-REV-05 | Confidentiality | Confidential reviewer comments must be restricted to authorized Admin/Editor users. |

## 7. Admin / Editor Requirements

| ID | Feature | Functional Requirement |
|---|---|---|
| FR-ADM-01 | Dashboard | Show core counts such as submissions, active reviews, articles and issues. |
| FR-ADM-02 | Submission Queue | List and filter manuscripts by workflow status. |
| FR-ADM-03 | Submission Detail | View manuscript metadata, files, authors, reviewers and editorial notes. |
| FR-ADM-04 | Reviewer Assignment | Assign one or more reviewers and set due dates. |
| FR-ADM-05 | Review Management | Record review results and monitor review status. |
| FR-ADM-06 | Editorial Decision | Record accept, minor revision, major revision or reject decisions. |
| FR-ADM-07 | Articles | Create, edit and publish article records. |
| FR-ADM-08 | Volumes / Issues | Create and manage volumes, issues, publication dates and issue files. |
| FR-ADM-09 | Editorial Board | Create, update, order and activate/deactivate board members. |
| FR-ADM-10 | Users | Manage author and admin accounts and roles. |
| FR-ADM-11 | Website Content | Edit and publish normal website content without developer involvement. |
| FR-ADM-12 | Announcements | Create, edit, publish and unpublish news, notices and calls for papers. |

### FR-ADM-11 Website Content Management

The Admin/Editor must be able to manage routine website content from a CMS-style interface.

Editable content:

- Home page sections and text
- About / Aim & Scope
- Author Guidelines
- Processing Charges
- Editorial Board
- Contact information
- Call for Papers
- News / Announcements
- Important links
- Footer content
- Journal metadata

Each content item should support:

`Edit → Preview → Save Draft → Publish → Unpublish`

No source-code changes should be required for these routine content updates.

## 8. DOI Management Requirements

| ID | Requirement |
|---|---|
| FR-DOI-01 | System generates a unique DOI-style identifier when the editor publishes an article or explicitly requests generation. |
| FR-DOI-02 | DOI must be unique and stored with the article. |
| FR-DOI-03 | DOI status must be stored separately from the DOI value. |
| FR-DOI-04 | Article page displays the DOI when available. |
| FR-DOI-05 | Admin can copy the DOI and DOI URL. |
| FR-DOI-06 | System must distinguish `Generated` from officially `Registered`. |
| FR-DOI-07 | If external DOI registration is later integrated, registration response/status must be stored. |

## 9. Manuscript Status Rules

Suggested workflow:

```text
Submitted
   ↓
Initial Review
   ↓
Reviewer Assigned
   ↓
Under Review
   ↓
Revision Required
   ↓
Revision Submitted
   ↓
Accepted / Rejected
   ↓
Published
```

The application must prevent invalid role actions.

Examples:

- An author cannot change editorial status.
- A reviewer cannot publish an article.
- A reviewer cannot see confidential information intended only for editors.
- An author can upload a revision only when revision is requested.
- Only authorized editors/admins can publish an article.

## 10. Database Functional Areas

- Users and roles
- Author and reviewer records/profiles
- Submissions and submission authors
- Submission files and revision versions
- Reviewer assignments and reviews
- Volumes, issues and published articles
- Article authors
- DOI information and status
- Editorial board
- Pages, news, indexing and charges
- Contact messages
- Settings
- Audit logs

## 11. Security / Access Requirements

- Use role-based access control for protected areas.
- Use secure password hashing and sessions.
- Use CSRF protection for state-changing forms.
- Use prepared SQL statements.
- Validate uploaded file type and size.
- Protect private reviewer comments and editorial notes from authors/public users.
- Record important administrative actions in an audit log.

## 12. Acceptance Criteria

- Each role can access only its permitted functions; public website content management is restricted to authorized Admin/Editor users.
- A manuscript can move through the defined editorial workflow.
- Reviewer feedback is visible to the correct audience.
- Authors can upload revisions only when requested.
- Editors can publish accepted manuscripts into an issue.
- A DOI-style identifier can be generated, stored and displayed.
- Public users can search and access published article metadata and PDFs.
- The UI remains simple and usable on desktop and mobile.
