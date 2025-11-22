# CargoOpt User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Core Features](#core-features)
4. [Container Management](#container-management)
5. [Item Management](#item-management)
6. [Running Optimizations](#running-optimizations)
7. [Viewing Results](#viewing-results)
8. [Ship Stowage Planning](#ship-stowage-planning)
9. [Export and Reporting](#export-and-reporting)
10. [Advanced Features](#advanced-features)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

---

## Introduction

### What is CargoOpt?

CargoOpt is an AI-powered container optimization system that uses advanced algorithms to solve 3D bin packing problems. It helps logistics companies, shipping operators, and warehouse managers maximize container utilization while respecting various constraints including:

- Weight distribution and stability
- Hazardous material segregation (IMDG compliance)
- Stacking limitations
- Temperature requirements
- Fragile item protection

### Key Benefits

- **Increased Utilization**: Achieve 70-90% space utilization rates
- **Cost Savings**: Reduce shipping costs by 15-30% through better packing
- **Environmental Impact**: Lower CO2 emissions by optimizing container usage
- **Safety Compliance**: Automatic validation of IMDG hazardous material regulations
- **Time Savings**: Automated optimization in seconds vs. hours of manual planning
- **Real-time Visualization**: Interactive 3D visualization of packing results

### System Requirements

**Web Application:**
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- Internet connection
- Minimum screen resolution: 1280x720

**Self-Hosted Deployment:**
- Python 3.8 or higher
- PostgreSQL 12 or higher
- 4GB RAM minimum (8GB recommended)
- Node.js 18+ (for frontend development)

---

## Getting Started

### Quick Start Guide

#### Step 1: Access the System

Navigate to the CargoOpt application:
```
https://your-domain.com/
```

Or for local development:
```
http://localhost:3000/
```

#### Step 2: Dashboard Overview

Upon login, you'll see the main dashboard with:
- **Recent Optimizations**: History of your past optimization runs
- **Quick Stats**: Performance metrics and utilization rates
- **Performance Chart**: Visual representation of optimization history
- **Getting Started Guide**: Quick links to common tasks

#### Step 3: Create Your First Optimization

1. Click **"New Optimization"** button
2. Define your container dimensions
3. Add items to pack
4. Configure optimization parameters
5. Run optimization
6. View results in 3D

### Understanding the Interface

#### Navigation Bar
- **Dashboard**: Main overview and optimization history
- **New Optimization**: Start a new packing optimization
- **Containers**: Manage container templates
- **Items**: Manage item library
- **History**: View past optimizations
- **Settings**: Configure system preferences

#### Dashboard Components

**Statistics Cards:**
- Total Optimizations
- Average Utilization
- Average Computation Time
- Success Rate

**Recent Optimizations Table:**
- Optimization ID
- Date and Time
- Container Size
- Items Packed
- Utilization Rate
- Status (Completed/Failed/Running)
- Actions (View/Delete)

---

## Core Features

### Container Optimization

The system supports various container types and sizes:

#### Standard Container Types

| Type | Dimensions (L×W×H mm) | Max Weight | Internal Volume |
|------|----------------------|------------|-----------------|
| 20ft Standard | 5898×2352×2393 | 28,180 kg | 33.2 m³ |
| 40ft Standard | 12032×2352×2393 | 26,680 kg | 67.7 m³ |
| 40ft High Cube | 12032×2352×2698 | 26,560 kg | 76.3 m³ |
| 45ft High Cube | 13556×2352×2698 | 27,700 kg | 86.0 m³ |
| 20ft Refrigerated | 5444×2294×2276 | 27,400 kg | 28.4 m³ |
| 40ft Refrigerated | 11583×2294×2544 | 26,960 kg | 67.5 m³ |

#### Custom Containers

You can define custom container dimensions:
- Length: 100-50,000 mm
- Width: 100-10,000 mm
- Height: 100-10,000 mm
- Max Weight: 1-100,000 kg

### Supported Item Types

CargoOpt handles various item categories:

- **Glass**: Fragile, requires careful handling
- **Wood**: Furniture, lumber, pallets
- **Metal**: Machinery parts, steel components
- **Plastic**: Containers, products
- **Electronics**: Computers, devices (fragile)
- **Textiles**: Clothing, fabrics
- **Food**: Packaged food items
- **Chemicals**: Hazardous materials
- **Other**: Miscellaneous cargo

### Storage Conditions

- **Standard**: Room temperature, no special requirements
- **Refrigerated**: 2°C to 8°C
- **Frozen**: -25°C to -18°C
- **Hazardous**: Special handling required

---

## Container Management

### Defining a Container

#### Step 1: Select Container Type

Choose from preset containers or select "Custom Dimensions":

```
Container Type: [Dropdown]
├── Custom Dimensions
├── 20ft Standard (5898 x 2352 x 2393 mm)
├── 40ft Standard (12032 x 2352 x 2393 mm)
├── 40ft High Cube (12032 x 2352 x 2698 mm)
└── 20ft Refrigerated (5444 x 2294 x 2276 mm)
```

#### Step 2: Enter Container Details

**Required Fields:**
- Length (mm)
- Width (mm)
- Height (mm)
- Maximum Weight (kg)

**Optional Fields:**
- Container Name/ID
- Container Type Classification
- Description

**Example:**
```json
{
  "container_id": "CONT001",
  "name": "20ft Standard Container A1",
  "length": 5898,
  "width": 2352,
  "height": 2393,
  "max_weight": 28180,
  "container_type": "standard"
}
```

### Container Templates

Save frequently used containers as templates:

1. Define container specifications
2. Click "Save as Template"
3. Enter template name
4. Access from "My Templates" section

### Container Validation

The system automatically validates:
- ✓ Dimensions are within acceptable ranges
- ✓ Weight capacity is realistic
- ✓ Volume calculations are correct
- ✗ Alerts if total item volume exceeds container

---

## Item Management

### Adding Items

#### Manual Entry

Click "Add Item" and enter details:

**Required Information:**
- Item Name/ID
- Length (mm)
- Width (mm)
- Height (mm)
- Weight (kg)

**Optional Information:**
- Quantity
- Item Type
- Fragile (Yes/No)
- Stackable (Yes/No)
- Maximum Stack Weight (kg)
- Rotation Allowed (Yes/No)
- Keep Upright (Yes/No)
- Priority (1-10, where 1 is highest)

**Example:**
```json
{
  "item_id": "BOX001",
  "name": "Electronics Box",
  "length": 400,
  "width": 300,
  "height": 250,
  "weight": 15.5,
  "quantity": 10,
  "item_type": "electronics",
  "fragile": true,
  "stackable": true,
  "max_stack_weight": 50,
  "rotation_allowed": true,
  "keep_upright": false,
  "priority": 1
}
```

#### Bulk Import via CSV

Import multiple items from a CSV file:

**CSV Format:**
```csv
name,length,width,height,weight,quantity,fragile,stackable
"Box A",1000,800,600,50,5,false,true
"Glass Panel",1200,900,50,40,3,true,false
"Metal Part",800,600,400,120,2,false,false
```

**Steps:**
1. Click "Import CSV"
2. Select your CSV file
3. Review imported items
4. Confirm import

#### Quick Add

For similar items, use "Quick Add":
1. Click "Quick Add"
2. Enter base item details
3. Specify number of variants
4. Adjust individual properties

### Item Properties Explained

#### Fragile Items
- Marked as fragile to prevent heavy items from being placed on top
- Automatically positioned in upper layers when possible
- Additional padding space may be allocated

#### Stackability
- **Stackable = Yes**: Other items can be placed on top
- **Stackable = No**: Nothing will be placed on top
- **Max Stack Weight**: Maximum weight that can be placed on top (kg)

#### Rotation
- **Rotation Allowed = Yes**: Item can be rotated for better fit
- **Keep Upright = Yes**: Item must maintain vertical orientation
- Rotations considered: 0°, 90°, 180°, 270°

#### Priority Levels
- **1-2**: Critical items, packed first
- **3-5**: Standard priority
- **6-8**: Lower priority
- **9-10**: Fill-in items, packed last

### Hazardous Materials

For hazardous items, specify:
- **IMDG Class**: Classification (1, 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 7, 8, 9)
- **UN Number**: Four-digit identification number
- **Proper Shipping Name**: Official designation

**IMDG Classes:**
- **Class 1**: Explosives
- **Class 2**: Gases (2.1 Flammable, 2.2 Non-flammable, 2.3 Toxic)
- **Class 3**: Flammable Liquids
- **Class 4**: Flammable Solids
- **Class 5**: Oxidizers
- **Class 6**: Toxic Substances
- **Class 7**: Radioactive Materials
- **Class 8**: Corrosives
- **Class 9**: Miscellaneous

**Automatic Segregation:**
The system automatically enforces segregation requirements between incompatible hazardous classes.

---

## Running Optimizations

### Optimization Workflow

#### Step 1: Configure Container
Define or select your container specifications

#### Step 2: Add Items
Add all items that need to be packed

#### Step 3: Choose Algorithm

**Genetic Algorithm (Recommended)**
- Best for: Medium to large problems (20-1000 items)
- Pros: Finds near-optimal solutions, handles complex constraints
- Cons: Longer computation time
- Typical time: 30-120 seconds

**Constraint Programming**
- Best for: Small problems (<20 items) with many constraints
- Pros: Fast, guarantees valid solutions
- Cons: May not find optimal solution for large problems
- Typical time: 10-30 seconds

**Hybrid Approach**
- Best for: Complex problems with mixed requirements
- Pros: Balances speed and quality
- Cons: Longer computation time
- Typical time: 60-180 seconds

**Auto-Select**
- System automatically chooses the best algorithm based on problem characteristics

#### Step 4: Set Optimization Objective

**Balanced (Recommended)**
- Equal emphasis on all factors
- Best for general use

**Maximum Space Utilization**
- Prioritize filling the container
- May sacrifice stability

**Maximum Stability**
- Prioritize center of gravity and weight distribution
- May result in lower space utilization

**Maximum Accessibility**
- Prioritize easy unloading
- Items placed for convenient access

#### Step 5: Advanced Parameters (Optional)

**Genetic Algorithm Parameters:**
- Population Size: 10-500 (default: 100)
- Generations: 5-500 (default: 50)
- Mutation Rate: 0-1 (default: 0.15)
- Crossover Rate: 0-1 (default: 0.85)

**Computation Settings:**
- Time Limit: 10-600 seconds (default: 300)

#### Step 6: Start Optimization

Click "Start Optimization" and monitor progress:
- Progress bar shows completion percentage
- Current generation/iteration displayed
- Best fitness score updated in real-time
- Estimated time remaining

### Interpreting Results

#### Metrics Summary

**Space Utilization**
```
Formula: (Used Volume / Container Volume) × 100%
Target: >75% is good, >85% is excellent
```

**Weight Utilization**
```
Formula: (Total Weight / Max Weight) × 100%
Target: <90% for safety margin
```

**Items Packed**
```
Shows: X of Y items packed
Goal: Pack all items if possible
```

**Computation Time**
```
Time taken to find solution
Typical: 30-120 seconds
```

**Fitness Score**
```
Range: 0-1 (1 is perfect)
Components:
- 40% Space Utilization
- 25% Stability
- 25% Constraint Satisfaction
- 10% Accessibility
```

#### Solution Quality

- **Score > 0.85**: Excellent solution
- **Score 0.70-0.85**: Good solution
- **Score 0.50-0.70**: Acceptable solution
- **Score < 0.50**: Poor solution, consider adjusting constraints

---

## Viewing Results

### 3D Visualization

The results viewer provides an interactive 3D view of the packed container:

#### Camera Controls

**Mouse Controls:**
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out

**Preset Views:**
- Front View
- Side View
- Top View
- Isometric View
- Reset Camera

#### Display Options

**Wireframe Mode**
- Toggle to see container and item edges
- Helps identify item boundaries

**Show Axes**
- Display X, Y, Z axes
- Helps understand orientation

**Show Labels**
- Display item names/IDs
- Helps identify specific items

**Container Opacity**
- Adjust transparency: 0-100%
- See items inside more clearly

#### Item Information

Click on any item to view:
- Item Name/ID
- Dimensions (L×W×H)
- Weight
- Position (X, Y, Z coordinates)
- Rotation angle
- Items stacked on top/below

### Results Tabs

#### Placements Tab

Table view of all placed items:

| # | Item | Position (X, Y, Z) | Dimensions | Weight | Rotation |
|---|------|-------------------|------------|--------|----------|
| 1 | Box A | 0, 0, 0 | 1000×800×600 | 50 kg | 0° |
| 2 | Box B | 1000, 0, 0 | 800×600×500 | 30 kg | 90° |

**Column Sorting:**
- Click column headers to sort
- Filter by item type, position, etc.

#### Statistics Tab

Detailed performance metrics:
- Algorithm used
- Fitness score breakdown
- Utilization by dimension
- Weight distribution
- Center of gravity coordinates
- Stability metrics

#### Violations Tab

Lists any constraint violations:
- **Critical**: Must be addressed
- **Warning**: Should be reviewed
- **Info**: Recommendations

Common violations:
- Item extends beyond container
- Overlap between items
- Insufficient support from below
- Weight limit exceeded
- Hazmat segregation violation

### Unpacked Items

If not all items fit, view unpacked items list:
- Item details
- Reason not packed
- Suggestions for fitting

---

## Ship Stowage Planning

### Vessel Configuration

Define vessel specifications:

**Basic Information:**
- Vessel Name
- IMO Number
- Type (Container Ship, Bulk Carrier, etc.)
- TEU Capacity

**Dimensions:**
- Length Overall (m)
- Breadth (m)
- Depth (m)
- Draft Design/Max (m)

**Capacity:**
- Deadweight Tonnage
- Gross Tonnage
- Reefer Plugs

**Compartments:**
- Number of Bays
- Number of Rows
- Tiers Above Deck
- Tiers Below Deck

### Creating Stowage Plans

#### Step 1: Select Vessel
Choose from your vessel fleet

#### Step 2: Add Containers
Import or manually add containers to be loaded

#### Step 3: Configure Loading
- Loading Port
- Discharge Port
- Voyage Number
- Departure/Arrival Times

#### Step 4: Run Optimization
System automatically:
- Assigns containers to bays/rows/tiers
- Ensures proper weight distribution
- Maintains stability (GM, trim, list)
- Segregates hazardous materials
- Groups refrigerated containers

#### Step 5: Review Plan
View 3D stowage visualization showing:
- Container positions by bay/row/tier
- Color coding by destination/type
- Reefer plug allocations
- Hazmat locations and segregation

### Bay Plans

View individual bay plans:
- Cross-section view
- Tier-by-tier breakdown
- Container IDs and details
- Weight distribution per bay

### Loading Sequence

Optimized loading sequence:
1. Heavy containers first (bottom tiers)
2. Hazardous materials with proper segregation
3. Refrigerated containers near power
4. Standard containers
5. Light/fragile containers on top

### Stability Calculations

Real-time stability metrics:
- **GM (Metacentric Height)**: Should be within acceptable range
- **Trim**: Difference between forward and aft draft
- **List**: Lateral inclination
- **Stress Calculations**: Hull stress distribution

---

## Export and Reporting

### Export Formats

#### PDF Report
Comprehensive report including:
- Executive summary
- 3D visualization snapshots
- Item placement table
- Statistics and metrics
- Violation reports
- Recommendations

**Options:**
- Page Size: A4, Letter, A3
- Include 3D Views: Yes/No
- Include Item List: Yes/No
- Include Statistics: Yes/No
- DPI: 72-600

#### JSON Data
Complete optimization data:
```json
{
  "optimization_id": "uuid",
  "container": {...},
  "items": [...],
  "placements": [...],
  "metrics": {...},
  "algorithm": "genetic",
  "parameters": {...}
}
```

#### CSV Export
Tabular data for spreadsheet analysis:
- Placements.csv: All item placements
- Statistics.csv: Performance metrics
- Violations.csv: Constraint violations

#### Excel Workbook
Multiple sheets:
- Summary
- Placements
- Items
- Statistics
- Charts

#### Image Export
High-resolution images:
- PNG (lossless, recommended)
- JPEG (smaller file size)
- Resolution: 72-600 DPI
- Custom dimensions

### Sharing Results

**Generate Shareable Link:**
- Create read-only link
- Set expiration date
- Password protection (optional)

**Email Report:**
- Send PDF directly
- Include multiple recipients
- Add custom message

**Print:**
- Browser print optimized
- Page breaks properly formatted
- Includes all sections

---

## Advanced Features

### Batch Optimization

Optimize multiple containers simultaneously:
1. Select "Batch Mode"
2. Add multiple container configurations
3. Run all optimizations
4. Compare results side-by-side

### Scenario Comparison

Compare different optimization approaches:
- Different algorithms
- Different objectives
- Different constraints
- Side-by-side visualization

### Templates and Presets

**Container Templates:**
- Save frequently used containers
- Quick access from dropdown
- Edit or delete anytime

**Item Libraries:**
- Build libraries of common items
- Categorize by project/customer
- Import entire libraries

**Optimization Presets:**
- Save algorithm configurations
- Quick-apply settings
- Share with team members

### API Integration

Integrate CargoOpt with your systems:

**REST API Endpoints:**
```
POST   /api/optimize          - Submit optimization
GET    /api/optimize/{id}     - Get results
GET    /api/containers        - List containers
POST   /api/containers        - Create container
GET    /api/items             - List items
POST   /api/items             - Create item
GET    /api/history           - Optimization history
POST   /api/exports/{id}      - Export results
```

**Authentication:**
```
Authorization: Bearer {your-api-key}
```

**Example Request:**
```bash
curl -X POST https://api.cargoopt.com/optimize \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "container": {...},
    "items": [...],
    "algorithm": "genetic"
  }'
```

### Environmental Impact Analysis

Calculate carbon footprint:
- CO2 emissions per shipment
- Savings from improved utilization
- Fuel consumption estimates
- Environmental rating (A+ to F)

**Emissions Report Includes:**
- Current emissions (kg CO2)
- Baseline comparison
- Potential savings
- Trees equivalent to offset
- Recommendations

---

## Best Practices

### Container Configuration

1. **Use Standard Sizes When Possible**
   - Preset containers are pre-validated
   - Faster setup
   - Industry-standard dimensions

2. **Account for Packing Materials**
   - Reduce internal dimensions by 50-100mm for dunnage
   - Consider pallets and padding

3. **Set Realistic Weight Limits**
   - Legal road limits: Typically 24,000-28,000 kg for 20ft
   - Include container tare weight

### Item Definition

1. **Accurate Measurements**
   - Measure packaging, not just product
   - Include pallets if applicable
   - Round up to nearest 10mm for safety margin

2. **Set Appropriate Priorities**
   - Priority 1-2: Fragile, valuable, hazardous
   - Priority 3-5: Standard items
   - Priority 6-10: Flexible, fill-in items

3. **Use Item Categories**
   - Consistent categorization helps optimization
   - Enables filtering and reporting

4. **Define Constraints Accurately**
   - Fragile items: Set stackable=false or low max_stack_weight
   - Upright items: Set keep_upright=true
   - Heavy items: Allow rotation for better placement

### Optimization Strategy

1. **Start with Balanced Objective**
   - Good starting point for most use cases
   - Adjust based on results

2. **Increase Generations for Better Results**
   - More generations = better solutions
   - Diminishing returns after 100 generations
   - Balance quality vs. time

3. **Use Hybrid for Complex Cases**
   - Many hazardous materials
   - Mixed fragile and heavy items
   - Temperature control requirements

4. **Review Unpacked Items**
   - Understand why items didn't fit
   - Adjust priorities or constraints
   - Consider additional container

### Safety and Compliance

1. **Hazardous Materials**
   - Always specify IMDG class
   - Verify segregation requirements
   - Check local regulations

2. **Weight Distribution**
   - Target center of gravity near container center
   - Avoid excessive front/back weight bias
   - Heavy items on bottom

3. **Fragile Items**
   - Place in upper tiers
   - Minimize stacking
   - Add extra padding (reduce dimensions)

4. **Refrigerated Items**
   - Group together
   - Ensure container supports reefer
   - Monitor temperature during transport

### Performance Optimization

1. **Break Large Problems into Batches**
   - 100-200 items per optimization
   - Run multiple smaller optimizations
   - Combine results manually if needed

2. **Use Auto-Select Algorithm**
   - System chooses optimal algorithm
   - Adapts to problem size
   - Generally good performance

3. **Set Reasonable Time Limits**
   - 60 seconds: Quick results
   - 120 seconds: Good balance
   - 300 seconds: Best quality

---

## Troubleshooting

### Common Issues

#### Issue: Low Utilization (<50%)

**Possible Causes:**
- Items too large for container
- Too many constraints (fragile, keep upright)
- Unrealistic priority settings

**Solutions:**
- Review item dimensions
- Reduce fragile constraints where possible
- Adjust priorities to be more balanced
- Consider larger container
- Remove low-priority items

#### Issue: Items Not Packing

**Check:**
1. Item dimensions vs. container dimensions
2. Total volume vs. container volume
3. Total weight vs. max weight
4. Rotation settings
5. Stacking constraints

**Solutions:**
- Enable rotation if not already
- Increase max stack weight
- Reduce keep_upright constraints
- Split into multiple containers

#### Issue: Optimization Takes Too Long

**Solutions:**
- Reduce number of items
- Decrease population size (50-75)
- Decrease generations (25-40)
- Set shorter time limit
- Use Constraint algorithm for small problems

#### Issue: Unstable Results

**Indicators:**
- High center of gravity
- Poor weight distribution
- Warnings in violations tab

**Solutions:**
- Use "Maximum Stability" objective
- Ensure heavy items have high priority
- Check max stack weights are realistic
- Reduce container fill target

#### Issue: Hazmat Violations

**Common Problems:**
- Incompatible classes too close
- Insufficient segregation distance
- Hazmat above/below restrictions violated

**Solutions:**
- Verify IMDG classes are correct
- Reduce number of different hazmat classes
- Use dedicated containers for hazmat
- Check segregation requirements

#### Issue: Cannot View 3D Visualization

**Troubleshooting:**
1. Check browser compatibility (Chrome, Firefox, Edge)
2. Enable JavaScript
3. Enable WebGL in browser
4. Update graphics drivers
5. Try different browser
6. Disable browser extensions

#### Issue: Export Fails

**Solutions:**
- Check file permissions
- Ensure sufficient disk space
- Try different format
- Reduce image resolution
- Contact support with optimization ID

### Error Messages

**"Validation failed"**
- Check all required fields are filled
- Verify dimensions are positive numbers
- Ensure weight values are realistic

**"Container volume exceeded"**
- Total item volume > container volume
- Remove items or use larger container

**"Weight limit exceeded"**
- Total item weight > container max weight
- Reduce item count or weight values

**"Optimization timeout"**
- Exceeded maximum computation time
- Reduce problem size or increase time limit

**"No valid solution found"**
- Constraints too restrictive
- Items physically cannot fit
- Relax some constraints or reduce items

### Getting Help

**Documentation:**
- User Guide (this document)
- API Documentation
- Algorithm Details

**Support Channels:**
- Email: support@cargoopt.com
- Help Desk: https://support.cargoopt.com
- Live Chat: Available in application
- Phone: +1-XXX-XXX-XXXX

**Community:**
- User Forum: https://forum.cargoopt.com
- Knowledge Base: https://kb.cargoopt.com
- Video Tutorials: https://youtube.com/cargoopt

**When Contacting Support, Provide:**
- Optimization ID
- Screenshot of issue
- Browser version and OS
- Description of problem
- Steps to reproduce

---

## Appendix

### Keyboard Shortcuts

- `Ctrl+N`: New Optimization
- `Ctrl+S`: Save
- `Ctrl+E`: Export
- `Ctrl+K`: Search
- `Escape`: Cancel/Go Back
- `?`: Show Help

### Glossary

**Bay**: Vertical section of a vessel for container stowage
**Center of Gravity (COG)**: Balance point of loaded container
**Constraint Programming**: Optimization method using logical rules
**DPI**: Dots Per Inch (image resolution)
**Fitness Score**: Overall quality metric (0-1)
**Genetic Algorithm**: Evolution-based optimization method
**GM (Metacentric Height)**: Vessel stability measurement
**IMDG**: International Maritime Dangerous Goods Code
**ISO Code**: Container size/type code
**List**: Lateral tilting of vessel
**Placement**: Position of item in container
**Row**: Lateral section in vessel bay
**Segregation**: Required separation of hazardous materials
**TEU**: Twenty-foot Equivalent Unit
**Tier**: Vertical layer in vessel bay
**Trim**: Fore-aft inclination of vessel
**Utilization**: Percentage of space/weight used

### Units of Measurement

**Length**: millimeters (mm)
**Weight**: kilograms (kg)
**Volume**: cubic meters (m³)
**Temperature**: Celsius (°C)

**Conversions:**
- 1 inch = 25.4 mm
- 1 foot = 304.8 mm
- 1 pound = 0.454 kg
- 1 m³ = 35.315 ft³

---

**CargoOpt User Guide - Version 1.0.0**  
*Last Updated: November 2024*  
*© 2024 CargoOpt Development Team. All rights reserved.*