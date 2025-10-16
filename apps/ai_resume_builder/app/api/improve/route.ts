import { NextRequest, NextResponse } from "next/server";

interface ImproveRequest {
  enhancementType: string;
  resumeText: string;
}

interface EnhancementSuggestion {
  section: string;
  original: string;
  suggestion: string;
  reasoning: string;
}

// Mock AI enhancement logic - in production this would call actual AI services
function generateMockSuggestions(
  enhancementType: string,
  resumeText: string,
): EnhancementSuggestion[] {
  const suggestions: EnhancementSuggestion[] = [];

  switch (enhancementType) {
    case "professional":
      suggestions.push({
        section: "Summary",
        original: "Software engineer with experience in web development",
        suggestion:
          "Results-driven Senior Software Engineer with 5+ years of experience architecting scalable web applications and leading cross-functional development teams",
        reasoning:
          "More professional tone with quantified experience and leadership emphasis",
      });
      break;
    case "keywords":
      suggestions.push({
        section: "Skills",
        original: "JavaScript, React, Node.js",
        suggestion:
          "JavaScript, TypeScript, React, Next.js, Node.js, Express, REST APIs, GraphQL, AWS, Docker, Kubernetes, CI/CD, Agile, Scrum",
        reasoning:
          "Added industry-standard keywords and technologies for better ATS compatibility",
      });
      break;
    case "impact":
      suggestions.push({
        section: "Experience",
        original: "Built web applications",
        suggestion:
          "Architected and delivered 3 mission-critical web applications serving 100K+ users, resulting in 40% improvement in user engagement",
        reasoning: "Quantified impact with specific metrics and results",
      });
      break;
    case "format":
      suggestions.push({
        section: "Experience",
        original: "• Built web applications\n• Led team meetings",
        suggestion:
          "• Architected scalable web applications using React and Node.js\n• Led cross-functional team of 5 developers in Agile environment\n• Implemented CI/CD pipeline reducing deployment time by 60%",
        reasoning:
          "Improved formatting with specific technologies and quantified achievements",
      });
      break;
  }

  return suggestions;
}

export async function POST(request: NextRequest) {
  try {
    const body: ImproveRequest = await request.json();
    const { enhancementType, resumeText } = body;

    // Validate input
    if (!enhancementType || !resumeText) {
      return NextResponse.json(
        { error: "enhancementType and resumeText are required" },
        { status: 400 },
      );
    }

    // Simulate AI processing delay
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Generate mock suggestions
    const suggestions = generateMockSuggestions(enhancementType, resumeText);

    return NextResponse.json({
      success: true,
      suggestions,
      enhancementType,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("Error in improve API:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 },
    );
  }
}

// Handle OPTIONS request for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
