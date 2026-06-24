interface SkillBadgeProps {
  skills: string | undefined | null;
}

export default function SkillBadge({ skills }: SkillBadgeProps) {
  if (!skills) {
    return <span className="text-slate-400 text-xs italic">Sin definir</span>;
  }

  const skillList = skills
    .split(',')
    .map((s) => s.trim())
    .filter((s) => s.length > 0);

  if (skillList.length === 0) {
    return <span className="text-slate-400 text-xs italic">Sin definir</span>;
  }

  return (
    <div className="flex flex-wrap gap-1">
      {skillList.map((skill, index) => (
        <span
          key={`${skill}-${index}`}
          className="bg-slate-100 text-slate-700 text-[11px] px-2.5 py-0.5 rounded-md font-semibold border border-slate-200/55 transition-all hover:bg-slate-200"
        >
          {skill}
        </span>
      ))}
    </div>
  );
}