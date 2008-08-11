;;; gud.el --- Grand Unified Debugger mode for running GDB and other debuggers

;; Author: Eric S. Raymond <esr@snark.thyrsus.com>
;; Maintainer: FSF
;; Keywords: unix, tools

;; Copyright (C) 1992, 1993, 1994, 1995, 1996, 1998, 2000, 2001, 2002, 2003,
;;  2004, 2005, 2006, 2007 Free Software Foundation, Inc.

;; This file is (not yet) part of GNU Emacs.

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

;; (global-set-key [f5] 'eval-buffer)

;; When we send a command to the debugger via gud-call, it's annoying
;; to see the command and the new prompt inserted into the debugger's
;; buffer; we have other ways of knowing the command has completed.
;;
;; If the buffer looks like this:
;; --------------------
;; (gdb) set args foo bar
;; (gdb) -!-
;; --------------------
;; (the -!- marks the location of point), and we type `C-x SPC' in a
;; source file to set a breakpoint, we want the buffer to end up like
;; this:
;; --------------------
;; (gdb) set args foo bar
;; Breakpoint 1 at 0x92: file make-docfile.c, line 49.
;; (gdb) -!-
;; --------------------
;; Essentially, the old prompt is deleted, and the command's output
;; and the new prompt take its place.
;;
;; Not echoing the command is easy enough; you send it directly using
;; process-send-string, and it never enters the buffer.  However,
;; getting rid of the old prompt is trickier; you don't want to do it
;; when you send the command, since that will result in an annoying
;; flicker as the prompt is deleted, redisplay occurs while Emacs
;; waits for a response from the debugger, and the new prompt is
;; inserted.  Instead, we'll wait until we actually get some output
;; from the subprocess before we delete the prompt.  If the command
;; produced no output other than a new prompt, that prompt will most
;; likely be in the first chunk of output received, so we will delete
;; the prompt and then replace it with an identical one.  If the
;; command produces output, the prompt is moving anyway, so the
;; flicker won't be annoying.
;;
;; So - when we want to delete the prompt upon receipt of the next
;; chunk of debugger output, we position gud-delete-prompt-marker at
;; the start of the prompt; the process filter will notice this, and
;; delete all text between it and the process output marker.  If
;; gud-delete-prompt-marker points nowhere, we leave the current
;; prompt alone.
(defvar gud-delete-prompt-marker nil)

(defvar gud-filter-pending-text nil
  "Non-nil means this is text that has been saved for later in `gud-filter'.")

(defvar gud-filter-defer-flag nil
  "Non-nil means don't process anything from the debugger right now.
It is saved for when this flag is not set.")

;; These functions are responsible for inserting output from your debugger
;; into the buffer.  The hard work is done by the method that is
;; the value of gud-marker-filter.

(defun gud-filter (proc string)
  ;; Here's where the actual buffer insertion is done
  (let (output process-window)
    (if (buffer-name (process-buffer proc))
	(if gud-filter-defer-flag
	    ;; If we can't process any text now,
	    ;; save it for later.
	    (setq gud-filter-pending-text
		  (concat (or gud-filter-pending-text "") string))

	  ;; If we have to ask a question during the processing,
	  ;; defer any additional text that comes from the debugger
	  ;; during that time.
	  (let ((gud-filter-defer-flag t))
	    ;; Process now any text we previously saved up.
	    (if gud-filter-pending-text
		(setq string (concat gud-filter-pending-text string)
		      gud-filter-pending-text nil))

	    (with-current-buffer (process-buffer proc)
	      ;; If we have been so requested, delete the debugger prompt.
	      (save-restriction
		(widen)
		(if (marker-buffer gud-delete-prompt-marker)
		    (let ((inhibit-read-only t))
		      (delete-region (process-mark proc)
				     gud-delete-prompt-marker)
		      (comint-update-fence)
		      (set-marker gud-delete-prompt-marker nil)))
		;; Save the process output, checking for source file markers.
		(setq output (xsh-marker-filter string))
		;; Check for a filename-and-line number.
		;; Don't display the specified file
		;; unless (1) point is at or after the position where output appears
		;; and (2) this buffer is on the screen.
		(setq process-window
		      (and gud-last-frame
			   (>= (point) (process-mark proc))
			   (get-buffer-window (current-buffer)))))

	      ;; Let the comint filter do the actual insertion.
	      ;; That lets us inherit various comint features.
	      (comint-output-filter proc output))

	    ;; Put the arrow on the source line.
	    ;; This must be outside of the save-excursion
	    ;; in case the source file is our current buffer.
	    (if process-window
		(with-selected-window process-window
		  (gud-display-frame))
	      ;; We have to be in the proper buffer, (process-buffer proc),
	      ;; but not in a save-excursion, because that would restore point.
	      (with-current-buffer (process-buffer proc)
		(gud-display-frame))))

	  ;; If we deferred text that arrived during this processing,
	  ;; handle it now.
	  (if gud-filter-pending-text
	      (gud-filter proc ""))))))

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

    (while (string-match "\n\032\032\\(.*\\)\n" xsh-marker-acc)
      (let ((match (match-string 1 xsh-marker-acc)))

	;; Pick up stopped annotation if attaching to process.
	(if (string-equal match "stopped") (setq xsh-active-process t))

	(when (string-equal match "completions")
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
  (add-hook 'comint-output-filter-functions
	  'xsh-marker-filter)
  ;(make-comint-in-buffer "name" "*shell*" "/home/epronk/stuff/shell-mode/proto.py")
  (comint-run "/home/epronk/stuff/shell-mode/proto.py")
  ;(set-process-filter (get-buffer-process buffer) 'gud-filter)
  )

(xsh-marker-filter "foo
pre-completions
foobar
foobaz
fooman
completions
")


(xsh-marker-filter "foo
pre-prompt
(gdb) 
prompt")

(xsh-marker-filter "foo
")

(xsh-marker-filter "pre-prompt
")
(xsh-marker-filter "(gdb) 
")
(xsh-marker-filter "pre-prompt
")
prompt")

