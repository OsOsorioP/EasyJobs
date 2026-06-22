import { Edit2, Trash2, Mail, Phone } from 'lucide-react';
import type { Candidate } from '../../../types';
import SkillBadge from './SkillBadge';

interface CandidateRowProps {
  candidate: Candidate;
  canModify: boolean;
  canDelete: boolean;
  onEdit: (candidate: Candidate) => void;
  onDelete: (id: string) => void;
}

export default function CandidateRow({
  candidate,
  canModify,
  canDelete,
  onEdit,
  onDelete,
}: CandidateRowProps) {
  return (
    <tr className="hover:bg-slate-50/50 transition-colors border-b border-slate-100 last:border-none">
      <td className="py-4 px-6">
        <p className="font-bold text-slate-800">{candidate.name}</p>
        <div className="flex flex-col gap-0.5 mt-1 text-xs text-slate-500">
          <span className="flex items-center gap-1.5">
            <Mail className="w-3.5 h-3.5 text-slate-400" /> 
            {candidate.email}
          </span>
          {candidate.phone && (
            <span className="flex items-center gap-1.5">
              <Phone className="w-3.5 h-3.5 text-slate-400" /> 
              {candidate.phone}
            </span>
          )}
        </div>
      </td>
      <td className="py-4 px-6">
        <SkillBadge skills={candidate.skills} />
      </td>
      <td className="py-4 px-6">
        <p className="text-slate-700 font-medium line-clamp-1">
          {candidate.experience || 'No registrada'}
        </p>
        {candidate.summary && (
          <p className="text-xs text-slate-400 truncate mt-1 max-w-xs">
            {candidate.summary}
          </p>
        )}
      </td>
      {canModify && (
        <td className="py-4 px-6 text-right">
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={() => onEdit(candidate)}
              title="Editar Perfil"
              className="p-1.5 text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 rounded transition-colors cursor-pointer"
            >
              <Edit2 className="w-4 h-4" />
            </button>
            {canDelete && (
              <button
                onClick={() => onDelete(candidate.id)}
                title="Eliminar de forma permanente"
                className="p-1.5 text-rose-600 hover:text-white bg-rose-50 hover:bg-rose-600 rounded transition-colors cursor-pointer"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </td>
      )}
    </tr>
  );
}