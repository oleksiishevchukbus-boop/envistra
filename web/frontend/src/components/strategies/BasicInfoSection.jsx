function BasicInfoSection({ editForm, disabled, onUpdateField }) {
  return (
    <div className="mb-4 bg-navy-900/60 border border-primary-800/30 rounded-lg p-4">
      <h4 className="text-sm font-mono text-gray-400 mb-3">Basic Info</h4>
      <div className="grid grid-cols-3 gap-4">
      <div>
        <label className="block text-xs font-mono text-gray-500 mb-1">Name</label>
        <input
          type="text"
          value={editForm.name}
          onChange={(e) => onUpdateField('name', e.target.value)}
          disabled={disabled}
          className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
        />
      </div>
      <div>
        <label className="block text-xs font-mono text-gray-500 mb-1">Description</label>
        <input
          type="text"
          value={editForm.description}
          onChange={(e) => onUpdateField('description', e.target.value)}
          disabled={disabled}
          className="w-full px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
        />
      </div>
      <div>
        <label className="block text-xs font-mono text-gray-500 mb-1">Color</label>
        <div className="flex gap-2">
          <input
            type="color"
            value={editForm.color}
            onChange={(e) => onUpdateField('color', e.target.value)}
            disabled={disabled}
            className="w-10 h-10 bg-navy-800 border border-primary-800/50 rounded cursor-pointer disabled:opacity-50"
          />
          <input
            type="text"
            value={editForm.color}
            onChange={(e) => onUpdateField('color', e.target.value)}
            disabled={disabled}
            className="flex-1 px-3 py-2 bg-navy-800 border border-primary-800/50 rounded text-gray-200 font-mono text-sm disabled:opacity-50"
          />
        </div>
      </div>
      </div>
    </div>
  )
}

export default BasicInfoSection
