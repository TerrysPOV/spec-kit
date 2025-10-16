"use client";

import { useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";

interface EnhancementSuggestion {
  section: string;
  original: string;
  suggestion: string;
  reasoning: string;
}

export default function AIEnhancer() {
  const [suggestions, setSuggestions] = useState<EnhancementSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [enhancementType, setEnhancementType] = useState("professional");

  const enhancementTypes = [
    { value: "professional", label: "Professional Tone" },
    { value: "keywords", label: "ATS Keywords" },
    { value: "impact", label: "Quantified Impact" },
    { value: "format", label: "Format & Structure" },
  ];

  const handleEnhance = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/improve", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          enhancementType,
          resumeText: "Sample resume content...", // This would come from uploaded resume
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      } else {
        alert("Failed to get AI suggestions");
      }
    } catch (error) {
      alert("Error getting AI suggestions");
    } finally {
      setIsLoading(false);
    }
  };

  const applySuggestion = (suggestion: EnhancementSuggestion) => {
    // In a real app, this would update the resume content
    console.log("Applying suggestion:", suggestion);
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        AI Enhancement
      </h3>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Enhancement Type
          </label>
          <select
            value={enhancementType}
            onChange={(e) => setEnhancementType(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {enhancementTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleEnhance}
          disabled={isLoading}
          className="w-full btn-primary disabled:opacity-50 flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Analyzing...</span>
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4" />
              <span>Enhance Resume</span>
            </>
          )}
        </button>

        {suggestions.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">AI Suggestions</h4>
            {suggestions.map((suggestion, index) => (
              <div
                key={index}
                className="border border-gray-200 rounded-lg p-3"
              >
                <div className="flex justify-between items-start mb-2">
                  <h5 className="font-medium text-sm text-gray-900">
                    {suggestion.section}
                  </h5>
                  <button
                    onClick={() => applySuggestion(suggestion)}
                    className="text-xs btn-primary"
                  >
                    Apply
                  </button>
                </div>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-500">Original: </span>
                    <span className="text-gray-700">{suggestion.original}</span>
                  </div>
                  <div>
                    <span className="text-green-600 font-medium">
                      Suggestion:{" "}
                    </span>
                    <span className="text-gray-700">
                      {suggestion.suggestion}
                    </span>
                  </div>
                  <div>
                    <span className="text-blue-600">Reasoning: </span>
                    <span className="text-gray-600">
                      {suggestion.reasoning}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
