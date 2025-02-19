
def parse_somatic_variants(text):
    # Split text into lines
    lines = text.split('\n')
    
    # Initialize variables to track whether we're in the right section
    capturing_data = False
    parsed_entries = []
    header_passed = False
    
    for line in lines:
        stripped_line = line.strip()

        if "None identified" in stripped_line:
            break
        
        # Check if we have reached our target section
        if "Variants of probable somatic origin (somatic mutations)" in stripped_line:
            capturing_data = True  # We've found the start of our desired section
            header_passed = False  # Reset to ensure header is not captured
            continue

        # If we are within the correct section but have reached a blank line or another section, stop parsing
        elif not stripped_line and capturing_data:
            break
        
        # Only parse lines when we're within our target section
        if capturing_data:
            # Skip the header line after identifying the start of the section
            if not header_passed and (stripped_line == "Gene DNA change Protein change Location VAF Type" or stripped_line == "Gene DNA Protein Location VAF Type"):
                header_passed = True  # We've successfully passed the header
                continue

            # Split line into components using any whitespace as delimiter
            parts = stripped_line.split()
            # print(len(parts))
            if len(parts) < 3:
                break
            
            # Extract fields, accounting for special cases in protein change or type
            gene = parts[0]
            dna_change = parts[1]

            # Protein change might be followed by additional descriptive text, like "(Boundary Exon 14)"
            protein_info = ' '.join(parts[2:4])
            if not protein_info.startswith("p."):
                break
            protein_change_end_index = len(protein_info) - protein_info[::-1].find('p.') - 3
            protein_change = protein_info[:protein_change_end_index + 3]
            protein_change = protein_change.split(" ")[0]

            # Locate VAF by searching for '%' in parts
            vaf_start_index = next((i for i, part in enumerate(parts) if '%' in part), len(parts))
            vaf = parts[vaf_start_index] if vaf_start_index < len(parts) else None

            # Type might be multi-field, capture everything after the last known field
            if len(parts) < 6:
                type_field = "Unknown"
            else:
                type_field = ' '.join(parts[vaf_start_index + 1:])
            
            # Create a dictionary for this entry
            parsed_entry = {
                "Gene": gene,
                "DNA change": dna_change,
                "Protein change": protein_change.strip(),
                "VAF": vaf,
                "Type": type_field.strip()
            }
            # print(parsed_entry)
            
            # Append to results list
            parsed_entries.append(parsed_entry)
    
    return parsed_entries
