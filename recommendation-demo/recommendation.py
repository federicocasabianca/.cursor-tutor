from mock_dataset import load_materials

def recommend_materials(preferred_category, preferred_grade, max_price):
    """
    Recommend teaching materials based on:
      - preferred_category: subject (e.g., 'Mathematik')
      - preferred_grade: grade level (e.g., '3. Klasse')
      - max_price: maximum price threshold
    """
    materials = load_materials()
    recommendations = []
    for material in materials:
        # For simplicity, we use 'category' as the subject and 'class_grade' as the grade.
        # We also assume the provided material has a numeric price.
        material_category = material.get("category", "").lower() if material.get("category") else ""
        material_grade = material.get("class_grade")
        
        # Convert inputs to lowercase for case-insensitive comparison
        preferred_category_lower = preferred_category.lower() if preferred_category else ""
        
        if (material_category == preferred_category_lower and
            material_grade == preferred_grade and
            material.get("price", 0) <= max_price):
            recommendations.append(material)
    return recommendations

if __name__ == "__main__":
    # Example: Recommend 'Mathematik' materials for '3. Klasse' with a price up to 5.00.
    recommended = recommend_materials("Mathematik", "3. Klasse", 5.0)
    print("Recommended Materials:")
    for item in recommended:
        print(item)