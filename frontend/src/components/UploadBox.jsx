import { useRef, useState } from 'react'
import { UploadCloud } from 'lucide-react'

export default function UploadBox({ onFile, disabled }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  const pick = (file) => {
    if (file) onFile(file)
  }

  return (
    <div
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault()
        setDragging(true)
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDragging(false)
        if (!disabled) pick(e.dataTransfer.files?.[0])
      }}
      className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-3xl border-2 border-dashed px-6 py-12 text-center ${
        dragging ? 'border-cyan-400 bg-cyan-500/10' : 'border-slate-700 bg-slate-900/60 hover:border-slate-500'
      } ${disabled ? 'cursor-not-allowed opacity-60' : ''}`}
    >
      <UploadCloud className="h-10 w-10 text-cyan-400" />
      <p className="text-slate-200">Drag & drop an image here, or click to browse</p>
      <p className="text-sm text-slate-500">JPG, PNG, WEBP up to 10 MB. You also get a Grad-CAM heat-map.</p>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => {
          pick(e.target.files?.[0])
          e.target.value = ''
        }}
      />
    </div>
  )
}
