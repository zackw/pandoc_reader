-- Pandoc filter: if we are generating HTML, replace each Math element
-- with the result of running KaTeX on its contents.  This requires
-- the command-line "katex" program to be installed at rendering time,
-- but does not require any JavaScript to be executed on the reader's
-- browser.  (The built-in --katex mode makes the opposite tradeoff.)
if FORMAT:match 'html' then
   have_math = false

   function Math(elem)
      local function trim(s)
         return s:gsub("^%s+", ""):gsub("%s+$", "")
      end

      have_math = true

      local katex_args = {'--no-throw-on-error'}
      if elem.mathtype == 'DisplayMath' then
         table.insert(katex_args, '--display-mode')
      end

      return pandoc.RawInline(
         FORMAT, trim(pandoc.pipe("katex", katex_args, trim(elem.text))))
   end

   function Meta(data)
      -- Pandoc currently has problems with boolean values in metadata,
      -- so instead the "has_math" property is absent when there is no math
      -- and the string "true" when there is math.
      -- See <https://github.com/jgm/pandoc/issues?q=6288+6630+6650>.
      if have_math then
        data.has_math = "true"
      end
      return data
   end
end
