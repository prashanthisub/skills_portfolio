* Load Bangladesh baseline dataset
use "Bangladesh_baseline_girls.dta"

* Filter for married respondents
keep if bl_ever_married == 1

* Plot histogram of age distribution for girls aged 10-18
histogram bl_age_reported if bl_age_reported >= 10 & bl_age_reported <= 18, frequency start(10) width(1) color(blue) title("Histogram of Reported Ages of Married Girls at Baseline") xtitle("Ages of Married Girls") normopts(lcolor(green) lwidth(thick))


* Save figure
graph save "Graph" "Baseline_Married_Distribution.gph"

* Load Bangladesh midline dataset
use "Bangladesh_midline_girls.dta"

* Filter for married respondents
keep if ml_ever_married == 1

* Plot histogram of age distribution for girls aged 10-18
histogram age if age >= 10 & age <= 18, frequency start(10) width(1) color(blue) title("Histogram of Reported Ages of Married Girls at Midline") xtitle("Ages of Married Girls") normopts(lcolor(green) lwidth(thick))

* Save figure
graph save "Graph" "Midline_Married_Distribution.gph"

* Load Bangladesh baseline dataset
use "Bangladesh_baseline_girls.dta"

* Filter for unmarried respondents
keep if bl_ever_married == 2

* Plot histogram of age distribution for girls aged 10-18
histogram bl_age_reported if bl_age_reported >= 10 & bl_age_reported <= 18, frequency start(10) width(1) color(blue) title("Histogram of Reported Ages of Unmarried Girls at Baseline") xtitle("Ages of Unmarried Girls") normopts(lcolor(green) lwidth(thick)))

* Save figure
graph save "Graph" "Baseline_Unmarried_Distribution.gph"

* Load Bangladesh midline dataset
use "Bangladesh_midline_girls.dta"

* Filter for unmarried respondents
keep if ml_ever_married == 2

* Plot histogram of age distribution for girls aged 10-18
histogram age if age >= 10 & age <= 18, frequency start(10) width(1) color(blue) title("Histogram of Reported Ages of Unmarried Girls at Midline") xtitle("Ages of Unmarried Girls") normopts(lcolor(green) lwidth(thick))

* Save figure
graph save "Graph" "Midline_Unmarried_Distribution.gph" 





