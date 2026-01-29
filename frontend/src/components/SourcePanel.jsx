import { useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Upload, Loader2, Image as ImageIcon } from "lucide-react";
import { useSourceStore } from '../stores/sourceStore';
import toast from 'react-hot-toast';

export default function SourcePanel() {
  const { sources, selectedSource, isUploading, addFileSource, selectSource } = useSourceStore();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);

  const handlePickFile = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const f = e.target.files[0];
    if (!f) return;

    if (f.type !== 'image/jpeg') {
      toast.error('Only JPG images are allowed');
      e.target.value = '';
      return;
    }

    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) return;
    await addFileSource(file);
    setFile(null);
    fileInputRef.current.value = '';
  };

  return (
    <div className="w-80 border-r h-full p-4 flex flex-col">
      <h2 className="font-semibold mb-4">Upload Marksheet</h2>

      {/* Hidden input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Upload box */}
      <div
        onClick={handlePickFile}
        className="border-2 border-dashed rounded-lg p-6 text-center cursor-pointer hover:bg-muted transition"
      >
        <ImageIcon className="mx-auto mb-2 text-muted-foreground" />
        <p className="text-sm">
          {file ? file.name : 'Click to select JPG file'}
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Only .jpg allowed
        </p>
      </div>

      <Button
        className="mt-3"
        disabled={!file || isUploading}
        onClick={handleUpload}
      >
        {isUploading ? (
          <>
            <Loader2 className="animate-spin mr-2" />
            Uploading…
          </>
        ) : (
          <>
            <Upload className="mr-2" />
            Upload JPG
          </>
        )}
      </Button>

      {/* Uploaded sources */}
      <div className="mt-6 space-y-2 flex-1 overflow-y-auto">
        {sources.map((s) => (

          <Card
            key={s._id}
            
            className={`p-2 cursor-pointer flex items-center ${
              selectedSource?._id === s._id ? 'bg-accent' : ''
            }`}
            onClick={() => selectSource(s)}
          >
            {s.title}
          </Card>
        ))}
      </div>
    </div>
  );
}
