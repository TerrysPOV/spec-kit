import ResumeUpload from "@/components/ResumeUpload";
import AIEnhancer from "@/components/AIEnhancer";
import ResumePreview from "@/components/ResumePreview";

export default function Home() {
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Professional Resume Enhancement
        </h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload your resume, enhance it with AI-powered suggestions, and
          preview the results before downloading.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <section id="upload">
            <ResumeUpload />
          </section>
          <section id="enhance">
            <AIEnhancer />
          </section>
        </div>
        <div className="lg:sticky lg:top-8">
          <section id="preview">
            <ResumePreview />
          </section>
        </div>
      </div>
    </div>
  );
}
