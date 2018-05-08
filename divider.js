Divider.translateHint = function(locale, string) {

    if (locale === 'en')
        return string;
    
    //TODO(danielhollas): i18n: \\text{} markup should be outside of this function. Or Maybe add it automatically to the input string? Probably not.
    var stringTranslations = {
        ' with a remainder of ': {
            'cs': ' se zbytkem '
        },
        
        'The remainder is 0, so we have our answer.': {
            'cs': 'Zbytek je 0, takže máme výsledek!'
        },
        
        '\\text{Since } %(remainder)s \\text{ is less than } %(divisor)s \\text{, it is left as our remainder.}': {
            'cs': '%(remainder)s \\text{ je menší než } %(divisor)s \\text{, takže nám zůstane jako zbytek.}'
        },
        
        'R': { // as in 'Remainder'
            'cs': '\\text{zb. }\~\~'
        },
        
        '\\text{How many times does }%(divisor)s\\text{ go into }\\color{#6495ED}{%(value)s}\\text{?}': {
            'cs' : "\\text{Kolikrát se vejde }%(divisor)s\\text{ do  }\\color{#6495ED}{%(value)s}\\text{?}"
        },
        
        'Write in a decimal and a zero.': {
            'cs': 'Napiš desetinnou čárku a nulu.'
        },
        
        "Shift the decimal 1 to the right.": {
            'cs': 'TODO-cs: Untranslated'
        },
        "Shift the decimal %(num)s to the right.": {
            'cs': 'TODO-cs: Untranslated'
        },
        
        "Bring the decimal up into the": {
            'cs': 'TODO-cs: Untranslated'
        },
        
        "answer (the quotient).": {
            'cs': 'TODO-cs: Untranslated'
        }
    };
    
    if (!(string in stringTranslations)) {
        return "ERROR: missing translation!";
    } else if (!(locale in stringTranslations[string])) {
        return 'ERROR: missing translation for locale '+locale
    }
    
    return stringTranslations[string][locale];
};

function Divider(locale, divisor, dividend, deciDivisor, deciDividend, decimalRemainder) {
    var graph = KhanUtil.currentGraph;
    var digitsDivisor = KhanUtil.integerToDigits(divisor);
    var digitsDividend = KhanUtil.integerToDigits(dividend);
    deciDivisor = deciDivisor || 0;
    deciDividend = deciDividend || 0;

    deciDividend = Divider.processDividend(digitsDividend, deciDividend);
    var deciDiff = deciDivisor - deciDividend;
    var hints = Divider.getHints(divisor, digitsDividend, deciDivisor, deciDividend, decimalRemainder);
    var numHints = hints.length;
    var divSign = "\\div";
    var divSigns = {
        ":": ["cs", "pl"]
    };
    
    for (key in divSigns) {
        for (var i = 0; i < divSigns[key].length; i++) {
            if (locale === divSigns[key][i]) {
                divSign = key;
            }
        }
    }

    var highlights = [];
    var leadingZeros = [];
    var decimals = [];
    var temporaryLabel = false;
    var index = 0;
    var dx = 0;
    var dy = 0;
    var currentValue = 0;
    var fOnlyZeros = true;
    var fFirstResult = true;
    
    //DH EDIT:
    var dxMinus = 0.0;
    var dxHint = 0.0;
    var dxResult = 0.0;
    var dyResult = 1.0;
    var dxRemainder = 0.0;

    this.show = function() {
        // Count number of subdivisions shown and find how many decimals have been added
        var steps = 0;
        var decimalsAdded = 0;
        for (var i = 0; i < hints.length; i++) {
            if (hints[i][0] === 'result' && hints[i][1] !== 0) {
                steps++;
            } else if (hints[i][0] === 'decimal-remainder') {
                decimalsAdded = hints[i][1];
            }
        }

        var paddedDivisor = digitsDivisor;
        if (deciDivisor !== 0) {
            paddedDivisor = (KhanUtil.padDigitsToNum(digitsDivisor.reverse(), deciDivisor + 1)).reverse();
        }
        
        // Calculate the x-coordinate for the hints
        // DH EDIT: We need to account for the equal sign
        // and we also need to account for the fact that we switched the
        // position of divisor and dividend
        
        dx = decimalsAdded + Math.max(0, deciDiff) + 0.5;
        var dxSmall = 0;
        // DH EDIT
        if (locale === 'en') {
            dxMinus = paddedDivisor.length;
            dx += digitsDividend.length;
            dxRemainder = digitsDividend.length;
        } else {
            dxMinus = digitsDividend.length-1.25;
            dx += paddedDivisor.length + 2.25;
            dxSmall = 0.75;
            dxHint = -digitsDividend.length+1.5;
            dxResult = dx - 0.2+1.0;
            dyResult = 0.0;
            dy = 1.0;
            dxRemainder = -dxHint + dx + 2.5;
        }
        
        graph.init({
            range: [[-1 - dxMinus, 17], [-2 * steps - 1, 2]],
            scale: [20, 40]
        });

        graph.style({
            fill: "#000"
        }, function() {
            if (deciDivisor !== 0) {
                decimals = decimals.concat(
                    graph.label([-1 - deciDivisor, -0.1],
                        "\\LARGE{" + decimalPointSymbol + "}", "center", true));
            }
            if (deciDividend !== 0) {
                decimals = decimals.concat(
                    graph.label(
                        [digitsDividend.length - deciDividend - 0.5, -0.1],
                        "\\LARGE{" + decimalPointSymbol + "}", "center", true));
            }
        });

       
        //DH edit
        if (locale === 'en') {
            drawDigits(paddedDivisor, -0.5 - dxMinus, 0);
            drawDigits(digitsDividend, 0, 0);
            graph.path([[-0.75, -0.5], [-0.75, 0.5], [dx - 0.8, 0.5]]);
        } else {
            drawDigits(digitsDividend, -0.5 - dxMinus + dxSmall, 0);
            graph.label([dxSmall, 0],
                "\\LARGE{"+ divSign + "" + divisor + "} =",
                "right");
        }
    };

    this.showHint = function() {
        this.clearArray(highlights);
        var hint = hints.shift();

        // For the last hint, remove leading zero in the answer
        // DH EDIT: This needs to be handled better
        if (hints.length === 0 || locale != 'en') {
            this.clearArray(leadingZeros);
        }

        switch (hint[0]) {
            case 'shift':
                this.shiftDecimals();
                break;
            case 'bring-up-decimal':
                this.bringUpDecimal();
                break;
            case 'division':
                currentValue = hint[1];
                this.showDivisionStep();
                break;
            case 'result':
                this.showDivisionStepResult(hint[1], hint[2], hint[3]);
                break;
            case 'decimal-remainder':
                this.addDecimalRemainder();
                break;
            case 'remainder':
                this.showRemainder(hint[1]);
                break;
        }
    };

    this.shiftDecimals = function() {
        this.clearArray(decimals);

        temporaryLabel = graph.label([dx, 1],
            $.ngettext("\\text{" + Divider.translateHint(locale, "Shift the decimal 1 to the right.")+"}",
                       "\\text{" + Divider.translateHint(locale, "Shift the decimal %(num)s to the right.")+"}",
                       deciDivisor),
            "right");

        this.addDecimals([[-1, -0.1], [digitsDividend.length + deciDiff - 0.5, -0.1]]);

        // Draw extra zeros in the dividend
        if (deciDiff > 0) {
            digitsDividend = KhanUtil.padDigitsToNum(digitsDividend, digitsDividend.length + deciDiff);
            var x = digitsDividend.length - deciDiff;
            var zeros = digitsDividend.slice(x);
            drawDigits(zeros, x, 0);
            highlights = highlights.concat(drawDigits(zeros, x, 0, KhanUtil.PINK));
        }
    };

    this.bringUpDecimal = function() {
        if (temporaryLabel) {
            temporaryLabel.remove();
            temporaryLabel = false;
        }

        // TODO(jeresig): i18n: This probably won't work in multiple langs
        graph.label([dx, 1.2], $._("\\text{" + Divider.translateHint("Bring the decimal up into the")+"}"), "right");
        graph.label([dx, 0.8], $._("\\text{"+Divider.translateHint("answer (the quotient).")+"}"), "right");
        this.addDecimals([[digitsDividend.length + deciDiff - 0.5, 0.9]]);
    };

    this.showDivisionStep = function(division) {
        // Write question
        var question = $._(Divider.translateHint(locale, '\\text{How many times does }%(divisor)s\\text{ go into }\\color{#6495ED}{%(value)s}\\text{?}'),
                        {divisor: divisor, value: currentValue});

        if (currentValue >= divisor) {
            graph.label([dx, dy], question, "right");
        } else {
            highlights = highlights.concat(graph.label([dx, dy], question, "right"));
        }
        
        // Bring down another number
        //DH EDIT, remove those weird zeros for now
        if (!fOnlyZeros) {
            graph.style({
                arrows: "->"
            }, function() {
                //DH EDIT: added dxHint to index, seems to work for en as well?? Need to check!
                highlights.push(graph.path([[index+dxHint, -0.5], [index+dxHint, dy + 0.5]]));
            });

            if (digitsDividend[index]) {
                drawDigits([digitsDividend[index]], index+dxHint, dy);
            } else {
                // Add a zero in the dividend and bring that down
                // DH I do not understand this, so commenting out for now
                if (locale === 'en')
                    drawDigits([0], index, 0);
                drawDigits([0], index+dxHint, dy);
            }
        }

        // Highlight current dividend
        var digits = KhanUtil.integerToDigits(currentValue);
        highlights = highlights.concat(drawDigits(digits, index - digits.length + 1+dxHint, dy, KhanUtil.BLUE));
    };

    this.showDivisionStepResult = function(result, remainder) {
        if (result !== 0) {
            fOnlyZeros = false;
        }
        
        if (locale === 'cs' && ! fOnlyZeros && fFirstResult) {
            graph.path([[dxHint+0.5+index, 0.1], [dxHint+0.5+index, 0.4], [dxHint+index, 0.4]]);
            fFirstResult = false;
        }
        
        // Leading zeros except one before a decimal point and those after
        // are stored separately so they can be removed later.
        // DH EDIT
        if (fOnlyZeros && index < digitsDividend.length + deciDiff - 1) {
            leadingZeros = leadingZeros.concat(drawDigits([0], index+dxResult, dyResult));
            // Highlight result
            highlights = highlights.concat(drawDigits([result], index+dxResult, dyResult, KhanUtil.GREEN));
            //DH EDIT, need to account for missing initial zeros in next steps
            if (locale != 'en') {
                dxResult -= 1;
            }
            
        } else {
            
            drawDigits([result], index+dxResult, dyResult);
            // Highlight result
            highlights = highlights.concat(drawDigits([result], index+dxResult, dyResult, KhanUtil.GREEN));
            
        }


        if (result !== 0) {
            if (dy>0) {
                dy -= 1;
            }
            dy -= 2;
            var productDigits = KhanUtil.integerToDigits(result * divisor);
            var productLength = productDigits.length;
            drawDigits(productDigits, index - productLength + 1+dxHint, dy + 1);

            graph.path([[index - productLength - 0.25+dxHint, dy + 0.5], [index + 0.5+dxHint, dy + 0.5]]);
            graph.label([index - productLength+dxHint, dy + 1] , "-");

            var remainderDigits = KhanUtil.integerToDigits(remainder);
            var remainderX = index - remainderDigits.length + 1 + dxHint;
            drawDigits(remainderDigits, remainderX, dy);
            highlights = highlights.concat(drawDigits(remainderDigits, remainderX, dy, KhanUtil.PINK));
            
            
            graph.label([dx, dy + 1],
                "\\blue{" + currentValue + "}" +
                divSign + divisor + "=" +
                "\\green{" + result + "}" +
                "\\text{" + $._(Divider.translateHint(locale, ' with a remainder of ')) + " }" +
                "\\pink{" + remainder + "}",
                "right");
        }
        index++;
    };

    this.addDecimalRemainder = function() {
        digitsDividend = KhanUtil.integerToDigits(dividend * 10);
        deciDividend = 1;
        deciDiff = deciDivisor - deciDividend;

        drawDigits([0], index, 0);
        this.addDecimals([[index - 0.5, 0.9], [index - 0.5, -0.1]]);
        
        var txt_en = 'Write in a decimal and a zero.'
        graph.label([dx, 1], $._('\\text{'+Divider.translateHint(locale, txt_en)+'}'), "right");
    };

    this.showRemainder = function(remainder) {
        var txt, txt_en;
        if (remainder === 0) {
            txt_en = "The remainder is 0, so we have our answer.";
            txt = "\\text{" + $._(Divider.translateHint(locale, txt_en)) + "}";
        } else {
            txt_en = '\\text{Since } %(remainder)s \\text{ is less than } %(divisor)s \\text{, it is left as our remainder.}';
            txt = $._(Divider.translateHint(locale, txt_en),
                    { remainder: remainder, divisor: divisor });
            var remainderShorthand = '\\text{' + Divider.translateHint(locale, "R") + "}";
            
            //TODO(danielhollas): (i18n): remainder is not positioned optimally when there are leading zeros
            drawDigits([remainderShorthand].concat(KhanUtil.integerToDigits(remainder)), dxRemainder, dyResult);
        }

        graph.label([dx, dy], txt, "right");
    };

    this.getNumHints = function() {
        return numHints;
    };

    this.clearArray = function(arr) {
        while (arr.length) {
            arr.pop().remove();
        }
    };

    this.addDecimals = function(coords) {
        graph.style({
                fill: "#000"
            }, function() {
                for (var i = 0; i < coords.length; i++) {
                    graph.label(coords[i], "\\LARGE{" + decimalPointSymbol + "}", "center", true);
                }
            });
    };

}

Divider.processDividend = function(dividendDigits, deciDividend) {
    // Trim unnecessary zeros after the decimal point
    var end = dividendDigits.length - 1;
    for (var i = 0; i < deciDividend; i++) {
        if (dividendDigits[end - i] === 0) {
        dividendDigits.splice(end - i);
        deciDividend--;
        } else {
            break;
        }
    }

    // Add zeros before the decimal point
    var extraZeros = deciDividend - dividendDigits.length + 1;
    for (var i = 0; i < extraZeros; i++) {
        dividendDigits.splice(0, 0, 0);
    }

    return deciDividend;
};

Divider.getNumberOfHints = function(divisor, dividend, deciDivisor, deciDividend, decimalRemainder) {
   var digitsDividend = KhanUtil.integerToDigits(dividend);
   deciDividend = Divider.processDividend(digitsDividend, deciDividend);
   var hints = Divider.getHints(divisor, digitsDividend, deciDivisor,  deciDividend, decimalRemainder);
   return hints.length;
};
// Go through the division step-by-step
// Return steps as an array of arrays,
// where the first item is the type of hint and following items are parameters.
// The hint types are:
// ['shift']                        The divisor is a decimal, so shift the decimal to make it an integer.
// ['bring-up-decimal']             The dividend is a decimal, so bring up decimal point into the quotient.
// ['decimal-remainder', param1]    decimalRemainder is true and we need to add decimals to the dividend to continue.
//                                  Param1 is the number of zeros added (to a maximum of 4).
//                                  e.g. for 1 / 8, we add a decimal and 3 zeros so 1 becomes 1.000.
// ['division', param1]             Show a sub-division step, dividing param1 by the divisor.
//                                  e.g. For 58 / 2, the first step is to divide 5 (param1) by 2.
// ['result', param1, param2]       Show the result of a sub-division step. The result is param1 remainder param2.
//                                  e.g. For 5 / 2, param1 is 2 and param2 is 1.
// ['remainder', param1]            Show the remainder of param1 (Usually 0 showing we have finished).
// Appended to the end of the hints is the number of decimals added as part of the decimal-remainder step
Divider.getHints = function(divisor, digitsDividend, deciDivisor, deciDividend, decimalRemainder) {
    var hints = [];
    //var digitsDividend = KhanUtil.integerToDigits(dividend);
    var dividend = 0;

    if (deciDivisor > 0) {
        hints.push(['shift']);
        if (deciDivisor > deciDividend) {
            digitsDividend = KhanUtil.padDigitsToNum(digitsDividend, digitsDividend.length + deciDivisor - deciDividend);
        }
    }

    if (deciDividend > deciDivisor) {
        hints.push(['bring-up-decimal']);
    }

    // If we want a decimal remainder, add up to 5 extra places
    var numPlaces = digitsDividend.length + (decimalRemainder ? 5 : 0);
    var digits = KhanUtil.padDigitsToNum(digitsDividend, numPlaces);
    var decimalsAdded = 0;
    var decimalsRemainder = ['decimal-remainder', 0];

    for (var i = 0; i < digits.length; i++) {
        if (i >= digitsDividend.length) {
            if (dividend === 0) {
                // No need to add more decimals
                break;
            } else {
                decimalsAdded++;
            }

            if (i === digitsDividend.length) {
                hints.push(decimalsRemainder);
            }
        }

        if (decimalsAdded > 0) {
            decimalsRemainder[1] = decimalsAdded;
        }

        dividend = dividend * 10 + digits[i];
        hints.push(['division', dividend]);

        var quotient = Math.floor(dividend / divisor);
        var product = divisor * quotient;
        dividend -= product;
        hints.push(['result', quotient, dividend]);
    }

    if (dividend === 0 || decimalsAdded !== 5) {
        hints.push(['remainder', dividend]);
    }

    return hints;
};

var decimalPointSymbol = icu.getDecimalFormatSymbols().decimal_separator;
decimalPointSymbol = ','
var DIVISOR = 20;
var DIVIDEND = 4;
var QUOTIENT = 0.2;
var DUMMY = [null,null,null,null,null,null,null];
var dummy = undefined;
var LOCALE= 'cs';

    graph.divider = new Divider(LOCALE, DIVISOR, DIVIDEND, 0, 0, true);
    
    DUMMY = Array( graph.divider.getNumHints() );
                
                graph.divider.show();
            var dummy = undefined;
                graph.divider.showHint();
            var dummy = undefined;
                graph.divider.showHint();
            var dummy = undefined;
                graph.divider.showHint();            
            var dummy = undefined;
                graph.divider.showHint();
            var dummy = undefined;
                graph.divider.showHint();
            var dummy = undefined;
                graph.divider.showHint();
            /*var dummy = undefined;
                graph.divider.showHint();
            var dummy = undefined;
                graph.divider.showHint();
            var dummy = undefined;
                graph.divider.showHint();

*/

