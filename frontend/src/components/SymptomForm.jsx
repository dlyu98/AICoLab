export function SymptomForm({ value, onChange, context, onContextChange, onSubmit, loading }) {
  return (
    <form className="panel" onSubmit={onSubmit}>
      <h2>Symptom Intake</h2>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Describe your symptoms, duration, and severity..."
        rows={5}
      />
      <div className="grid">
        <input
          placeholder="Age (optional)"
          value={context.age || ''}
          onChange={(e) => onContextChange('age', e.target.value)}
        />
        <input
          placeholder="Sex at birth (optional)"
          value={context.sex || ''}
          onChange={(e) => onContextChange('sex', e.target.value)}
        />
        <input
          placeholder="Medical history (optional)"
          value={context.history || ''}
          onChange={(e) => onContextChange('history', e.target.value)}
        />
      </div>
      <button disabled={loading} type="submit">{loading ? 'Analyzing...' : 'Get Guidance'}</button>
    </form>
  )
}
