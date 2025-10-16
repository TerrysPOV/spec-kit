"use client";

import { useState } from "react";
import { Download, Eye, FileText } from "lucide-react";

interface ResumeData {
  personalInfo: {
    name: string;
    email: string;
    phone: string;
    location: string;
  };
  summary: string;
  experience: Array<{
    title: string;
    company: string;
    duration: string;
    description: string;
  }>;
  skills: string[];
}

export default function ResumePreview() {
  const [resumeData, setResumeData] = useState<ResumeData>({
    personalInfo: {
      name: "John Doe",
      email: "john.doe@example.com",
      phone: "+1 (555) 123-4567",
      location: "San Francisco, CA",
    },
    summary:
      "Experienced software engineer with a passion for building scalable web applications and leading development teams.",
    experience: [
      {
        title: "Senior Software Engineer",
        company: "Tech Corp",
        duration: "2022 - Present",
        description:
          "Led development of microservices architecture serving 1M+ users daily.",
      },
    ],
    skills: ["React", "TypeScript", "Node.js", "Python", "AWS"],
  });

  const handleDownload = () => {
    // In a real app, this would generate and download a PDF
    alert("PDF download would be implemented here");
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Resume Preview</h3>
        <div className="flex space-x-2">
          <button className="btn-secondary flex items-center space-x-1">
            <Eye className="h-4 w-4" />
            <span>Preview</span>
          </button>
          <button
            onClick={handleDownload}
            className="btn-primary flex items-center space-x-1"
          >
            <Download className="h-4 w-4" />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      <div className="border rounded-lg p-6 bg-white max-h-96 overflow-y-auto">
        <div className="space-y-4">
          {/* Header */}
          <div className="text-center border-b pb-4">
            <h1 className="text-2xl font-bold text-gray-900">
              {resumeData.personalInfo.name}
            </h1>
            <div className="text-sm text-gray-600 mt-1">
              {resumeData.personalInfo.email} • {resumeData.personalInfo.phone}{" "}
              • {resumeData.personalInfo.location}
            </div>
          </div>

          {/* Summary */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Professional Summary
            </h2>
            <p className="text-gray-700 text-sm">{resumeData.summary}</p>
          </div>

          {/* Experience */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Experience
            </h2>
            <div className="space-y-3">
              {resumeData.experience.map((exp, index) => (
                <div key={index}>
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium text-gray-900">{exp.title}</h3>
                      <p className="text-sm text-blue-600">{exp.company}</p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {exp.duration}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mt-1">
                    {exp.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Skills */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">Skills</h2>
            <div className="flex flex-wrap gap-2">
              {resumeData.skills.map((skill, index) => (
                <span
                  key={index}
                  className="inline-block bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          This is a preview. Click &ldquo;Download PDF&rdquo; to generate the final version.
        </p>
      </div>
    </div>
  );
}
