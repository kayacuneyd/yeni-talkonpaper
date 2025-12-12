-- Generated Database Schema (sqlite)

CREATE TABLE speakers (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  name TEXT NOT NULL,
  bio TEXT,
  affiliation TEXT,
  email TEXT,
  website TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_speakers_email ON speakers (email);
CREATE INDEX idx_speakers_name ON speakers (name);

CREATE TABLE papers (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  title TEXT NOT NULL,
  abstract TEXT,
  authors TEXT NOT NULL,
  venue TEXT,
  publication_year INTEGER,
  doi TEXT,
  arxiv_id TEXT,
  pdf_object_key TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_papers_title ON papers (title);
CREATE INDEX idx_papers_doi ON papers (doi);
CREATE INDEX idx_papers_arxiv_id ON papers (arxiv_id);
CREATE INDEX idx_papers_publication_year ON papers (publication_year);

CREATE TABLE talks (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  paper_id INTEGER UNIQUE NOT NULL,
  speaker_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  duration_minutes INTEGER,
  talk_date DATE,
  venue_name TEXT,
  venue_location TEXT,
  video_object_key TEXT,
  audio_object_key TEXT,
  slides_object_key TEXT,
  thumbnail_object_key TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_talks_paper_id ON talks (paper_id);
CREATE INDEX idx_talks_speaker_id ON talks (speaker_id);
CREATE INDEX idx_talks_talk_date ON talks (talk_date);
CREATE INDEX idx_talks_title ON talks (title);

