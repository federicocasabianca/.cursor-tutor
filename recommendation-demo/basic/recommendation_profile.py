from mock_dataset import load_materials

def advanced_recommendation(preferred_grade, preferred_category, price_lower, price_upper, only_standalone=True):
    """
    Recommend teaching materials based on:
      - preferred_grade: the user's most frequently interacted grade level (e.g., "4. Klasse")
      - preferred_category: the user's most frequently interacted subject (e.g., "Biologie")
      - price_lower: the lower bound of the desired price range (e.g., 3.0)
      - price_upper: the upper bound of the desired price range (e.g., 5.0)
      - only_standalone: if True, exclude bundle materials.
      
    Returns:
      A list of recommended materials sorted by bestseller_rating in descending order.
    """
    materials = load_materials()
    recommendations = []
    
    for material in materials:
        # For simplicity, we use 'category' as the subject and 'class_grade' as the grade.
        # We assume that the material has a numeric price.
        material_category = material.get("category", "").lower() if material.get("category") else ""
        material_grade = material.get("class_grade")
        
        # Convert preferred_category to lowercase for case-insensitive comparison.
        preferred_category_lower = preferred_category.lower() if preferred_category else ""
        
        if (material_category == preferred_category_lower and
            material_grade == preferred_grade and
            price_lower <= material.get("price", 0) <= price_upper):
            
            # Exclude bundle materials if only_standalone is True.
            if only_standalone and material.get("is_bundle", False):
                continue
            
            recommendations.append(material)
    
    # Sort recommendations by bestseller_rating in descending order.
    recommendations.sort(key=lambda m: m.get("bestseller_rating", 0), reverse=True)
    return recommendations

if __name__ == "__main__":
    # Example usage:
    # Suppose a user has indicated a preference for grade "4. Klasse" and subject "Biologie",
    # and we want to recommend standalone materials priced between 3.0 and 5.0.
    user_preferred_grade = "4. Klasse"
    user_preferred_category = "Mathematik"
    user_price_lower = 1.0
    user_price_upper = 7.0

    recommended_items = advanced_recommendation(user_preferred_grade, user_preferred_category, user_price_lower, user_price_upper, only_standalone=True)
    
    print("Recommended Materials:")
    for item in recommended_items:
        title = item.get("title", "No Title")
        price = item.get("price", "N/A")
        bestseller_rating = item.get("bestseller_rating", "N/A")
        print(f"{title} - Price: {price} - Bestseller Rating: {bestseller_rating}")