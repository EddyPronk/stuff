;;; gud.el --- Grand Unified Debugger mode for running GDB and other debuggers

;; Author: Eric S. Raymond <esr@snark.thyrsus.com>
;; Maintainer: FSF
;; Keywords: unix, tools

;; Copyright (C) 1992, 1993, 1994, 1995, 1996, 1998, 2000, 2001, 2002, 2003,
;;  2004, 2005, 2006, 2007 Free Software Foundation, Inc.

;; This file is part of GNU Emacs.

;; GNU Emacs is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation; either version 2, or (at your option)
;; any later version.

;; GNU Emacs is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with GNU Emacs; see the file COPYING.  If not, write to the
;; Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
;; Boston, MA 02110-1301, USA.

;;; Commentary:

;; The ancestral gdb.el was by W. Schelter <wfs@rascal.ics.utexas.edu> It was
;; later rewritten by rms.  Some ideas were due to Masanobu.  Grand
;; Unification (sdb/dbx support) by Eric S. Raymond <esr@thyrsus.com> Barry
;; Warsaw <bwarsaw@cen.com> hacked the mode to use comint.el.  Shane Hartman
;; <shane@spr.com> added support for xdb (HPUX debugger).  Rick Sladkey
;; <jrs@world.std.com> wrote the GDB command completion code.  Dave Love
;; <d.love@dl.ac.uk> added the IRIX kluge, re-implemented the Mips-ish variant
;; and added a menu. Brian D. Carlstrom <bdc@ai.mit.edu> combined the IRIX
;; kluge with the gud-xdb-directories hack producing gud-dbx-directories.
;; Derek L. Davies <ddavies@world.std.com> added support for jdb (Java
;; debugger.)

;;; Code:

(defvar xsh-marker-regexp
  ;; This used to use path-separator instead of ":";
  ;; however, we found that on both Windows 32 and MSDOS
  ;; a colon is correct here.
  (concat "\032\032\\(.:?[^" ":" "\n]*\\)" ":"
	  "\\([0-9]*\\)" ":" ".*\n"))

;; There's no guarantee that Emacs will hand the filter the entire
;; marker at once; it could be broken up across several strings.  We
;; might even receive a big chunk with several markers in it.  If we
;; receive a chunk of text which looks like it might contain the
;; beginning of a marker, we save it here between calls to the
;; filter.
(defvar xsh-marker-acc "")
(make-variable-buffer-local 'xsh-marker-acc)

(defun xsh-marker-filter (string)
  (setq xsh-marker-acc (concat xsh-marker-acc string))
  (let ((output ""))

    ;; Process all the complete markers in this chunk.
    (while (string-match xsh-marker-regexp xsh-marker-acc)
      (setq

       ;; Extract the frame position from the marker.
       gud-last-frame (cons (match-string 1 xsh-marker-acc)
			    (string-to-number (match-string 2 xsh-marker-acc)))

       ;; Append any text before the marker to the output we're going
       ;; to return - we don't include the marker in this text.
       output (concat output
		      (substring xsh-marker-acc 0 (match-beginning 0)))

       ;; Set the accumulator to the remaining text.
       xsh-marker-acc (substring xsh-marker-acc (match-end 0))))

    ;; Check for annotations and change gud-minor-mode to 'gdba if
    ;; they are found.
    (while (string-match "\n\032\032\\(.*\\)\n" xsh-marker-acc)
      (let ((match (match-string 1 xsh-marker-acc)))

	;; Pick up stopped annotation if attaching to process.
	(if (string-equal match "stopped") (setq gdb-active-process t))

	;; Using annotations, switch to gud-gdba-marker-filter.
	(when (string-equal match "prompt")
	  (comint-dynamic-list-completions
	   (split-string (substring xsh-marker-acc 0 (match-beginning 0)))))

	(setq
	 ;; Append any text before the marker to the output we're going
	 ;; to return - we don't include the marker in this text.
	 output (concat output
			(substring xsh-marker-acc 0 (match-beginning 0)))

	 ;; Set the accumulator to the remaining text.

	 xsh-marker-acc (substring xsh-marker-acc (match-end 0)))

	;; Pick up any errors that occur before first prompt annotation.
	(if (string-equal match "error-begin")
	    (put-text-property 0 (length xsh-marker-acc)
			       'face font-lock-warning-face
			       xsh-marker-acc))))

    ;; Does the remaining text look like it might end with the
    ;; beginning of another marker?  If it does, then keep it in
    ;; xsh-marker-acc until we receive the rest of it.  Since we
    ;; know the full marker regexp above failed, it's pretty simple to
    ;; test for marker starts.
    (if (string-match "\n\\(\032.*\\)?\\'" xsh-marker-acc)
	(progn
	  ;; Everything before the potential marker start can be output.
	  (setq output (concat output (substring xsh-marker-acc
						 0 (match-beginning 0))))

	  ;; Everything after, we save, to combine with later input.
	  (setq xsh-marker-acc
		(substring xsh-marker-acc (match-beginning 0))))

      (setq output (concat output xsh-marker-acc)
	    xsh-marker-acc ""))

    output))

(defun xsh (&optional buffer)
  (interactive)
  (setq buffer (get-buffer-create (or buffer "*shell*")))
  (pop-to-buffer buffer)
  (make-comint-in-buffer "name" "*shell*" "/home/epronk/annotation/proto.py"))

(xsh-marker-filter "foo
pre-prompt
foobar
foobaz
fooman
prompt
")
