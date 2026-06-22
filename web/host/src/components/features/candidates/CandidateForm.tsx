import { useState, useEffect } from 'react';
import { Mail, Phone, FileText, Code, Briefcase } from 'lucide-react';
import type { Candidate, CandidateFormData } from '../../../types';

interface CandidateFormProps {
  editingCandidate: Candidate | null;
  onSubmit: (data: CandidateFormData) => Promise<void | boolean>;
  onCancel: () => void;
}

export default function CandidateForm({ editingCandidate, onSubmit, onCancel }: CandidateFormProps) {
  const [formData, setFormData] = useState<CandidateFormData>({
    name: '',
    email: '',
    phone: null,
    summary: null,
    skills: null,
    experience: null,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (editingCandidate) {
      setFormData({
        name: editingCandidate.name,
        email: editingCandidate.email,
        phone: editingCandidate.phone || null,
        summary: editingCandidate.summary || null,
        skills: editingCandidate.skills || null,
        experience: editingCandidate.experience || null,
      });
    }
  }, [editingCandidate]);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es obligatorio';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'El correo es obligatorio';
    } else if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.email = 'El correo debe ser válido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value || null,
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      setFormData({
        name: '',
        email: '',
        phone: null,
        summary: null,
        skills: null,
        experience: null,
      });
      onCancel();
    } catch (error) {
      console.error('Error al guardar candidato:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 space-y-5">
      {/* Nombre */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-slate-700 mb-2">
          Nombre Completo *
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Juan Pérez García"
          className={`w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
            errors.name
              ? 'border-rose-300 focus:ring-rose-500 bg-rose-50'
              : 'border-slate-200 focus:ring-slate-900 focus:border-transparent'
          }`}
        />
        {errors.name && (
          <p className="mt-1 text-xs text-rose-600">{errors.name}</p>
        )}
      </div>

      {/* Email */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
          <Mail className="w-4 h-4 text-slate-500" />
          Correo Electrónico *
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="correo@ejemplo.com"
          className={`w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 transition-all ${
            errors.email
              ? 'border-rose-300 focus:ring-rose-500 bg-rose-50'
              : 'border-slate-200 focus:ring-slate-900 focus:border-transparent'
          }`}
        />
        {errors.email && (
          <p className="mt-1 text-xs text-rose-600">{errors.email}</p>
        )}
      </div>

      {/* Teléfono */}
      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
          <Phone className="w-4 h-4 text-slate-500" />
          Teléfono
        </label>
        <input
          type="tel"
          id="phone"
          name="phone"
          value={formData.phone || ''}
          onChange={handleChange}
          placeholder="+34 123 456 789"
          className="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all"
        />
      </div>

      {/* Resumen Profesional */}
      <div>
        <label htmlFor="summary" className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
          <FileText className="w-4 h-4 text-slate-500" />
          Resumen Profesional
        </label>
        <textarea
          id="summary"
          name="summary"
          value={formData.summary || ''}
          onChange={handleChange}
          placeholder="Breve descripción de tu perfil profesional..."
          rows={3}
          className="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all resize-none"
        />
      </div>

      {/* Habilidades */}
      <div>
        <label htmlFor="skills" className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
          <Code className="w-4 h-4 text-slate-500" />
          Habilidades Clave
        </label>
        <textarea
          id="skills"
          name="skills"
          value={formData.skills || ''}
          onChange={handleChange}
          placeholder="Ej: React, Node.js, TypeScript, PostgreSQL"
          rows={3}
          className="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all resize-none"
        />
        <p className="mt-1 text-xs text-slate-500">Separa las habilidades con comas</p>
      </div>

      {/* Experiencia */}
      <div>
        <label htmlFor="experience" className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-slate-500" />
          Experiencia Profesional
        </label>
        <textarea
          id="experience"
          name="experience"
          value={formData.experience || ''}
          onChange={handleChange}
          placeholder="Describe tu experiencia profesional..."
          rows={3}
          className="w-full px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all resize-none"
        />
      </div>

      {/* Botones de Acción */}
      <div className="flex gap-3 pt-4 border-t border-slate-100">
        <button
          type="submit"
          disabled={isSubmitting}
          className="flex-1 bg-slate-900 text-white hover:bg-slate-800 disabled:bg-slate-400 disabled:cursor-not-allowed font-semibold text-sm py-2.5 px-4 rounded-lg transition-all"
        >
          {isSubmitting ? 'Guardando...' : editingCandidate ? 'Actualizar Candidato' : 'Registrar Candidato'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1 bg-slate-100 text-slate-700 hover:bg-slate-200 disabled:bg-slate-100 disabled:cursor-not-allowed font-semibold text-sm py-2.5 px-4 rounded-lg transition-all"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
}