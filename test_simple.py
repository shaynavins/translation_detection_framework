"""
Simple Test Script - Matches Translation-detection-framework Test

Tests the full 3-stage hierarchical pipeline with the same English→Hindi
translation that the reference implementation uses.
"""

from core.graph import app
import json


def serialize_state(obj):
    """
    Convert Pydantic models to JSON-serializable dict.
    Recursively handles nested models.
    """
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif isinstance(obj, dict):
        return {k: serialize_state(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_state(v) for v in obj]
    else:
        return obj


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING FRAMEWORK_IMPLEMENTATION")
    print("=" * 70)
    print()
    
    # Same test sentence as Translation-detection-framework
    input_state = {
        "source": "The qualities that determine a subculture as distinct may be linguistic, aesthetic, religious, political, sexual, geographical, or a combination of factors.",
        
        "mt": "वे गुण जो किसी उप-संस्कृति को अलग बनाते हैं, जैसे कि भाषा, सौंदर्य, धर्म, राजनीति, यौन, भूगोल या कई सारे कारकों का मिश्रण हो सकते हैं.",
        
        "reference": "उपसंस्कृति को विशिष्ट रूप से निर्धारित करने वाले गुण भाषाई, सौंदर्य, धार्मिक, राजनीतिक, यौन, भौगोलिक या कारकों का संयोजन हो सकते हैं।",

        "round": 1,

        "max_rounds": 2,

    }
    
    print("Input:")
    print(f"Source: {input_state['source'][:80]}...")
    print(f"MT (Hindi): {input_state['mt'][:60]}...")
    print(f"Reference (Hindi): {input_state['reference'][:60]}...")
    print()
    print("=" * 70)
    print("Running evaluation pipeline...")
    print("This will execute 21 agents + 1 aggregation (may take 1-2 minutes)")
    print("=" * 70)
    print()
    
    # Run the pipeline
    result = app.invoke(input_state)
    
    print("✅ Pipeline completed!")
    print()
    
    # Serialize results
    serialized_result = serialize_state(result)
    
    # Save to file
    with open("test_result.json", "w", encoding="utf-8") as f:
        json.dump(serialized_result, f, indent=4, ensure_ascii=False)
    
    print("📄 Full results saved to: test_result.json")
    print()
    
    # Display summary
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print()
    
    agg = result.get("aggregation")
    
    if agg:
        print("Final Scores:")
        print(f"  • Accuracy Error:     {agg['accuracy_error']:.3f} ({agg['accuracy_error']*100:.1f}%)")
        print(f"  • Fluency Error:      {agg['fluency_error']:.3f} ({agg['fluency_error']*100:.1f}%)")
        print(f"  • Terminology Error:  {agg['terminology_error']:.3f} ({agg['terminology_error']*100:.1f}%)")
        print(f"  • Style Error:        {agg['style_error']:.3f} ({agg['style_error']*100:.1f}%)")
        print()
        print(f"Overall Error Probability: {agg['overall_error_probability']:.3f}")
        print(f"📊 Final Quality Score: {agg['final_quality_score_100']:.1f}/100")
        print()
        
        # Interpretation
        print("Interpretation:")
        if agg['accuracy_error'] < 0.2:
            print("  ✅ Accuracy: Good - meaning is preserved")
        else:
            print("  ❌ Accuracy: Issues - meaning may be distorted")
            
        if agg['fluency_error'] < 0.3:
            print("  ✅ Fluency: Good - natural target language")
        elif agg['fluency_error'] < 0.6:
            print("  ⚠️  Fluency: Moderate - some awkwardness")
        else:
            print("  ❌ Fluency: Poor - significant issues")
            
        if agg['style_error'] < 0.3:
            print("  ✅ Style: Good - appropriate register")
        elif agg['style_error'] < 0.6:
            print("  ⚠️  Style: Moderate - some mismatch")
        else:
            print("  ❌ Style: Poor - register mismatch detected")
    else:
        print("❌ No aggregation results found!")
    
    print()
    print("=" * 70)
    print("Stage 3 Verification Results:")
    print("=" * 70)
    print()
    
    # Show Stage 3 verification
    for category in ["accuracy", "fluency", "terminology", "style"]:
        stage3_key = f"{category}Stage3"
        stage3 = result.get(stage3_key)
        if stage3:
            print(f"{category.upper()}:")
            print(f"  Consistency: {stage3.consistencyScore:.0f}/100")
            print(f"  Errors Exist: {stage3.errorsExists}")
            print(f"  Reasoning: {stage3.existanceReasoning[:100]}...")
            print()
    
    print("=" * 70)
    print("✅ Test completed successfully!")
    print("Review test_result.json for detailed agent outputs.")
    print("=" * 70)
