import React, { useState } from 'react';
import { 
  X, AlertTriangle, Bug, CheckCircle2, Clock, User, Cog as MachineIcon, 
  MessageSquare, Paperclip, Send, History, Building2, Calendar, FileText, ArrowRight
} from 'lucide-react';
import { Issue, Worker } from '../types';

interface IssueDetailModalProps {
  issue: Issue | null;
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => void;
  currentWorker?: Worker;
}

export function IssueDetailModal({
  issue,
  isOpen,
  onClose,
  onRefresh,
  currentWorker
}: IssueDetailModalProps) {
  const [activeSubTab, setActiveSubTab] = useState<'comments' | 'attachments' | 'history'>('comments');
  
  // Status Change State
  const [newStatus, setNewStatus] = useState<string>('');
  const [statusNotes, setStatusNotes] = useState<string>('');
  const [resolutionText, setResolutionText] = useState<string>('');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  // New Comment State
  const [commentText, setCommentText] = useState('');
  const [isAddingComment, setIsAddingComment] = useState(false);

  // New Attachment State
  const [fileName, setFileName] = useState('');
  const [fileUrl, setFileUrl] = useState('');
  const [fileType, setFileType] = useState('document');
  const [isAddingAttachment, setIsAddingAttachment] = useState(false);
  const [showAttachForm, setShowAttachForm] = useState(false);

  if (!isOpen || !issue) return null;

  const handleStatusUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newStatus) return;
    setIsUpdatingStatus(true);
    try {
      const res = await fetch(`/api/v1/issues/${issue.id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          notes: statusNotes || undefined,
          changed_by_id: currentWorker?.id || issue.assigned_worker_id,
          resolution: resolutionText || undefined
        })
      });
      if (res.ok) {
        setStatusNotes('');
        setResolutionText('');
        setNewStatus('');
        onRefresh();
      }
    } catch (err) {
      console.error('Error updating status:', err);
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    setIsAddingComment(true);
    try {
      const res = await fetch(`/api/v1/issues/${issue.id}/comments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          comment_text: commentText,
          author_name: currentWorker?.full_name || 'System User',
          author_id: currentWorker?.id
        })
      });
      if (res.ok) {
        setCommentText('');
        onRefresh();
      }
    } catch (err) {
      console.error('Error adding comment:', err);
    } finally {
      setIsAddingComment(false);
    }
  };

  const handleAddAttachment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileName || !fileUrl) return;
    setIsAddingAttachment(true);
    try {
      const res = await fetch(`/api/v1/issues/${issue.id}/attachments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_name: fileName,
          file_url: fileUrl,
          file_type: fileType
        })
      });
      if (res.ok) {
        setFileName('');
        setFileUrl('');
        setShowAttachForm(false);
        onRefresh();
      }
    } catch (err) {
      console.error('Error adding attachment:', err);
    } finally {
      setIsAddingAttachment(false);
    }
  };

  const getPriorityBadge = (p: string) => {
    switch (p) {
      case 'CRITICAL': return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'HIGH': return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'MEDIUM': return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      default: return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const getStatusBadge = (s: string) => {
    switch (s) {
      case 'Open': return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'In Progress': return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'Waiting': return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      case 'Resolved': return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
      case 'Closed': return 'bg-slate-800 text-slate-400 border-slate-700';
      default: return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 bg-slate-950 border-b border-slate-800 flex items-start justify-between shrink-0">
          <div>
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <span className="font-mono text-xs text-amber-400 font-bold bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                {issue.issue_code}
              </span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getPriorityBadge(issue.priority)}`}>
                {issue.priority} PRIORITY
              </span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getStatusBadge(issue.status)}`}>
                STATUS: {issue.status.toUpperCase()}
              </span>
            </div>
            <h2 className="text-xl font-bold text-slate-100">{issue.title}</h2>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800 transition shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 overflow-y-auto flex-1">
          {/* Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-950/60 border border-slate-800/80 rounded-xl text-xs">
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-bold block mb-0.5">Machine</span>
              <span className="text-slate-200 font-medium flex items-center gap-1 truncate">
                <MachineIcon className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                {issue.machine ? issue.machine.name : 'General Facility'}
              </span>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-bold block mb-0.5">Department</span>
              <span className="text-slate-200 font-medium flex items-center gap-1 truncate">
                <Building2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                {issue.department}
              </span>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-bold block mb-0.5">Assigned Worker</span>
              <span className="text-slate-200 font-medium flex items-center gap-1 truncate">
                <User className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                {issue.assigned_worker ? issue.assigned_worker.full_name : 'Unassigned'}
              </span>
            </div>
            <div>
              <span className="text-slate-400 text-[10px] uppercase font-bold block mb-0.5">Target Due Date</span>
              <span className="text-slate-200 font-medium flex items-center gap-1 truncate">
                <Calendar className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                {issue.due_date ? new Date(issue.due_date).toLocaleDateString() : 'No Due Date'}
              </span>
            </div>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-amber-400" />
              <span>Issue Description</span>
            </h3>
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
              {issue.description}
            </div>
          </div>

          {/* Resolution Card if present */}
          {issue.resolution && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs text-emerald-200 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <span>Issue Resolution Logged</span>
              </div>
              <p className="text-slate-300">{issue.resolution}</p>
              {issue.resolution_time && (
                <p className="text-[10px] text-slate-400 pt-1">
                  Resolved on {new Date(issue.resolution_time).toLocaleString()}
                </p>
              )}
            </div>
          )}

          {/* Status Change Control Bar */}
          <div className="p-4 bg-slate-950/80 border border-slate-800 rounded-xl space-y-3">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-amber-400" />
              <span>Change Issue Status</span>
            </h3>
            <form onSubmit={handleStatusUpdate} className="space-y-3">
              <div className="flex items-center gap-2 flex-wrap">
                {['Open', 'In Progress', 'Waiting', 'Resolved', 'Closed'].map((st) => (
                  <button
                    key={st}
                    type="button"
                    onClick={() => setNewStatus(st)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold border transition ${
                      (newStatus || issue.status) === st
                        ? 'bg-amber-500 text-slate-950 border-amber-400 shadow'
                        : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200 hover:border-slate-700'
                    }`}
                  >
                    {st}
                  </button>
                ))}
              </div>

              {newStatus && newStatus !== issue.status && (
                <div className="space-y-2 pt-2 border-t border-slate-800 animate-in fade-in">
                  <input 
                    type="text" 
                    placeholder="Add audit note for this status change..."
                    value={statusNotes}
                    onChange={e => setStatusNotes(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                  {(newStatus === 'Resolved' || newStatus === 'Closed') && (
                    <textarea 
                      rows={2}
                      placeholder="Enter technical resolution summary..."
                      value={resolutionText}
                      onChange={e => setResolutionText(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500 resize-none"
                    />
                  )}
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={isUpdatingStatus}
                      className="bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold px-4 py-2 rounded-lg transition"
                    >
                      {isUpdatingStatus ? 'Updating...' : `Confirm Status -> ${newStatus}`}
                    </button>
                  </div>
                </div>
              )}
            </form>
          </div>

          {/* Sub-Tabs: Comments, Attachments, Status History */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
              <button
                onClick={() => setActiveSubTab('comments')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  activeSubTab === 'comments'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Comments ({issue.comments.length})</span>
              </button>
              <button
                onClick={() => setActiveSubTab('attachments')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  activeSubTab === 'attachments'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Paperclip className="w-3.5 h-3.5" />
                <span>Attachments ({issue.attachments.length})</span>
              </button>
              <button
                onClick={() => setActiveSubTab('history')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  activeSubTab === 'history'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <History className="w-3.5 h-3.5" />
                <span>Status History ({issue.status_history.length})</span>
              </button>
            </div>

            {/* TAB 1: COMMENTS */}
            {activeSubTab === 'comments' && (
              <div className="space-y-4">
                <form onSubmit={handleAddComment} className="flex gap-2">
                  <input 
                    type="text"
                    placeholder="Add a comment or operational update..."
                    value={commentText}
                    onChange={e => setCommentText(e.target.value)}
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                  <button
                    type="submit"
                    disabled={isAddingComment || !commentText.trim()}
                    className="bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 font-bold px-4 py-2 rounded-xl text-xs flex items-center gap-1 transition shrink-0"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Send</span>
                  </button>
                </form>

                <div className="space-y-3">
                  {issue.comments.length === 0 ? (
                    <p className="text-xs text-slate-500 text-center py-6">No comments added yet.</p>
                  ) : (
                    issue.comments.map((c) => (
                      <div key={c.id} className="p-3 bg-slate-950 border border-slate-800/80 rounded-xl space-y-1">
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="font-bold text-amber-400">{c.author_name}</span>
                          <span className="text-slate-500">{new Date(c.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-xs text-slate-200">{c.comment_text}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* TAB 2: ATTACHMENTS */}
            {activeSubTab === 'attachments' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h4 className="text-xs font-bold text-slate-300">File & Document Attachments</h4>
                  <button
                    type="button"
                    onClick={() => setShowAttachForm(!showAttachForm)}
                    className="text-xs text-amber-400 hover:text-amber-300 font-bold flex items-center gap-1"
                  >
                    <Paperclip className="w-3.5 h-3.5" />
                    <span>{showAttachForm ? 'Cancel' : 'Attach File'}</span>
                  </button>
                </div>

                {showAttachForm && (
                  <form onSubmit={handleAddAttachment} className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <input 
                        type="text" 
                        placeholder="File Name (e.g. pressure_log.pdf)"
                        value={fileName}
                        onChange={e => setFileName(e.target.value)}
                        className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                        required
                      />
                      <input 
                        type="text" 
                        placeholder="File URL or Link"
                        value={fileUrl}
                        onChange={e => setFileUrl(e.target.value)}
                        className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                        required
                      />
                    </div>
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={isAddingAttachment}
                        className="bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold px-4 py-1.5 rounded-lg transition"
                      >
                        {isAddingAttachment ? 'Adding...' : 'Save Attachment'}
                      </button>
                    </div>
                  </form>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {issue.attachments.length === 0 ? (
                    <p className="text-xs text-slate-500 col-span-2 text-center py-6">No attachments added yet.</p>
                  ) : (
                    issue.attachments.map((a) => (
                      <a 
                        key={a.id} 
                        href={a.file_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="p-3 bg-slate-950 border border-slate-800 hover:border-amber-500/50 rounded-xl flex items-center gap-3 transition group"
                      >
                        <Paperclip className="w-4 h-4 text-amber-400 shrink-0 group-hover:scale-110 transition" />
                        <div className="truncate flex-1">
                          <p className="text-xs font-bold text-slate-200 group-hover:text-amber-300 truncate">{a.file_name}</p>
                          <p className="text-[10px] text-slate-500">{new Date(a.uploaded_at).toLocaleDateString()}</p>
                        </div>
                      </a>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* TAB 3: STATUS HISTORY */}
            {activeSubTab === 'history' && (
              <div className="space-y-3">
                {issue.status_history.length === 0 ? (
                  <p className="text-xs text-slate-500 text-center py-6">No status history logged.</p>
                ) : (
                  issue.status_history.map((h) => (
                    <div key={h.id} className="p-3 bg-slate-950 border border-slate-800/80 rounded-xl space-y-1">
                      <div className="flex items-center justify-between text-[11px]">
                        <div className="flex items-center gap-1.5 font-bold text-slate-300">
                          <span className="text-slate-400">{h.from_status}</span>
                          <ArrowRight className="w-3 h-3 text-amber-400" />
                          <span className="text-amber-300">{h.to_status}</span>
                        </div>
                        <span className="text-slate-500">{new Date(h.changed_at).toLocaleString()}</span>
                      </div>
                      {h.notes && <p className="text-xs text-slate-400">{h.notes}</p>}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
