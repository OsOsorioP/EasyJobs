import { useState, useEffect, type FormEvent } from 'react';
import type { Candidate, CandidateFormData } from '../types';

interface UseCandidateFormProps {
  initialCandidate: Candidate | null;
  onSubmit: (payload: CandidateFormData) => Promise<boolean>;
  onSuccess: () => void;
}

export function useCandidateForm({
  initialCandidate,
  onSubmit,
  onSuccess,
}: UseCandidateFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [summary, setSummary] = useState('');
  const [skills, setSkills] = useState('');
  const [experience, setExperience] = useState('');
  const [validationError, setValidationError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (initialCandidate) {
      setName(initialCandidate.name || '');
      setEmail(initialCandidate.email || '');
      setPhone(initialCandidate.phone || '');
      setSummary(initialCandidate.summary || '');
      setSkills(initialCandidate.skills || '');
      setExperience(initialCandidate.experience || '');
    } else {
      setName('');
      setEmail('');
      setPhone('');
      setSummary('');
      setSkills('');
      setExperience('');
    }
    setValidationError('');
  }, [initialCandidate]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setValidationError('');

    if (!name.trim()) {
      setValidationError('El nombre completo es obligatorio.');
      return;
    }

    if (!email.trim() || !/\S+@\S+\.\S+/.test(email)) {
      setValidationError('Debe ingresar un correo electrónico válido.');
      return;
    }

    setIsSubmitting(true);

    const payload: CandidateFormData = {
      name: name.trim(),
      email: email.trim(),
      phone: phone.trim() || undefined,
      summary: summary.trim() || undefined,
      skills: skills.trim() || undefined,
      experience: experience.trim() || undefined,
    };

    const success = await onSubmit(payload);
    setIsSubmitting(false);

    if (success) {
      onSuccess();
    }
  };

  return {
    fields: { name, email, phone, summary, skills, experience },
    setters: { setName, setEmail, setPhone, setSummary, setSkills, setExperience },
    validationError,
    isSubmitting,
    handleSubmit,
  };
}