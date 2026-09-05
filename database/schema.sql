-- IJMMHRD Database Schema
-- International Journal of Multidisciplinary Modern Research and Development

CREATE DATABASE IF NOT EXISTS ijmmhrd CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ijmmhrd;

-- ============================================================
-- USERS & ROLES
-- ============================================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role ENUM('admin', 'editor', 'author') NOT NULL DEFAULT 'author',
    affiliation VARCHAR(500),
    phone VARCHAR(50),
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- SUBMISSIONS
-- ============================================================
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paper_id VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    abstract TEXT,
    keywords VARCHAR(500),
    research_area VARCHAR(255),
    status ENUM(
        'submitted', 'initial_review', 'reviewer_assigned',
        'under_review', 'revision_required', 'revision_submitted',
        'accepted', 'rejected', 'published'
    ) NOT NULL DEFAULT 'submitted',
    submitted_by_name VARCHAR(255) NOT NULL,
    submitted_by_email VARCHAR(255) NOT NULL,
    editor_notes TEXT,
    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decided_at DATETIME,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_email (submitted_by_email),
    INDEX idx_paper_id (paper_id)
) ENGINE=InnoDB;

CREATE TABLE submission_authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    affiliation VARCHAR(500),
    is_corresponding TINYINT(1) NOT NULL DEFAULT 0,
    author_order INT NOT NULL DEFAULT 1,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE submission_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type ENUM('manuscript', 'cover_letter', 'revision', 'supplementary') NOT NULL DEFAULT 'manuscript',
    version INT NOT NULL DEFAULT 1,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- REVIEWERS & REVIEWS
-- ============================================================
CREATE TABLE reviewers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    specialization VARCHAR(500),
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE review_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    reviewer_id INT NOT NULL,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    status ENUM('pending', 'completed', 'overdue', 'cancelled') NOT NULL DEFAULT 'pending',
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES reviewers(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL UNIQUE,
    recommendation ENUM('accept', 'minor_revision', 'major_revision', 'reject') NOT NULL,
    rating INT,
    comments_to_author TEXT,
    confidential_comments TEXT,
    reviewed_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assignment_id) REFERENCES review_assignments(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- PUBLICATION: VOLUMES, ISSUES, ARTICLES
-- ============================================================
CREATE TABLE volumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volume_number INT NOT NULL UNIQUE,
    year INT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    volume_id INT NOT NULL,
    issue_number INT NOT NULL,
    title VARCHAR(255),
    publication_date DATE,
    is_current TINYINT(1) NOT NULL DEFAULT 0,
    cover_path VARCHAR(500),
    FOREIGN KEY (volume_id) REFERENCES volumes(id) ON DELETE CASCADE,
    UNIQUE KEY uk_vol_issue (volume_id, issue_number)
) ENGINE=InnoDB;

CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT UNIQUE,
    issue_id INT,
    title VARCHAR(500) NOT NULL,
    abstract TEXT,
    keywords VARCHAR(500),
    article_id VARCHAR(50) UNIQUE,
    doi VARCHAR(255) UNIQUE,
    doi_status ENUM('pending', 'generated', 'registered') DEFAULT 'pending',
    page_start INT,
    page_end INT,
    pdf_path VARCHAR(500),
    published_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id) ON DELETE SET NULL,
    FOREIGN KEY (issue_id) REFERENCES issues(id) ON DELETE SET NULL,
    INDEX idx_doi (doi),
    INDEX idx_article_id (article_id)
) ENGINE=InnoDB;

CREATE TABLE article_authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    affiliation VARCHAR(500),
    author_order INT NOT NULL DEFAULT 1,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- CMS: PAGES, ANNOUNCEMENTS, SETTINGS
-- ============================================================
CREATE TABLE pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    slug VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    content LONGTEXT,
    status ENUM('draft', 'published') NOT NULL DEFAULT 'draft',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by INT,
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    is_published TINYINT(1) NOT NULL DEFAULT 0,
    publish_date DATE,
    created_by INT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE editorial_board (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    affiliation VARCHAR(500),
    board_role VARCHAR(100),
    photo_path VARCHAR(500),
    display_order INT NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE research_areas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    display_order INT NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB;

CREATE TABLE settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    is_read TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- AUDIT LOG
-- ============================================================
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_entity (entity_type, entity_id)
) ENGINE=InnoDB;

-- ============================================================
-- SEED DATA
-- ============================================================

-- Default admin (password: admin123 — change immediately)
INSERT INTO users (email, password_hash, full_name, role) VALUES
('admin@ijmmhrd.com', '$2b$12$LJ3m4ys3Lk0TSwMBQoXnzOUPmRqyZ5EqF9Y9V7qHJfBxZm0hW8Mq2', 'IJMMHRD Admin', 'admin');

-- Default settings
INSERT INTO settings (setting_key, setting_value) VALUES
('journal_name', 'International Journal of Multidisciplinary Modern Research and Development'),
('journal_abbr', 'IJMMHRD'),
('journal_issn', 'XXXX-XXXX'),
('journal_email', 'editor@ijmmhrd.com'),
('journal_url', 'https://ijmmhrd.com'),
('doi_prefix', '10.XXXXX'),
('publication_frequency', 'Monthly'),
('footer_text', '© 2026 IJMMHRD. All rights reserved.'),
('contact_address', ''),
('contact_phone', ''),
('contact_email', 'editor@ijmmhrd.com');

-- Default CMS pages
INSERT INTO pages (slug, title, content, status) VALUES
('about', 'About IJMMHRD', '<p>The International Journal of Multidisciplinary Modern Research and Development (IJMMHRD) is a peer-reviewed, open-access journal that publishes high-quality research across all disciplines.</p>', 'published'),
('aim-scope', 'Aim & Scope', '<p>IJMMHRD aims to provide a platform for researchers, scholars, and academicians to share their research findings across multiple disciplines.</p>', 'published'),
('author-guidelines', 'Author Guidelines', '<p>Authors are invited to submit original research papers, review articles, and short communications.</p>', 'published'),
('paper-format', 'Paper Format', '<p>Manuscripts should be prepared in accordance with the journal formatting guidelines.</p>', 'published'),
('how-to-publish', 'How to Publish', '<p>Follow these steps to publish your research with IJMMHRD.</p>', 'published'),
('processing-charges', 'Processing Charges', '<p>Details about article processing charges will be listed here.</p>', 'published'),
('home-intro', 'Home Introduction', '<p>Welcome to IJMMHRD — a leading multidisciplinary journal dedicated to advancing knowledge through rigorous peer-reviewed research.</p>', 'published'),
('call-for-papers', 'Call for Papers', '<p>IJMMHRD invites researchers to submit their original work for publication.</p>', 'published');

-- Sample research areas
INSERT INTO research_areas (name, display_order) VALUES
('Computer Science & Engineering', 1),
('Electronics & Communication', 2),
('Mechanical Engineering', 3),
('Civil Engineering', 4),
('Electrical Engineering', 5),
('Biotechnology', 6),
('Physics', 7),
('Chemistry', 8),
('Mathematics', 9),
('Management & Commerce', 10),
('Arts & Humanities', 11),
('Medical Sciences', 12),
('Environmental Science', 13),
('Social Sciences', 14),
('Education', 15);
