-- Pandoc filter: if we are generating HTML, replace each Math element
-- with the result of running KaTeX on its contents.  This requires
-- the command-line "katex" program to be installed at rendering time,
-- but does not require any JavaScript to be executed on the reader's
-- browser.  (The built-in --katex mode makes the opposite tradeoff.)
if FORMAT:match 'html' then
   function Math(elem)
      local function trim(s)
         return s:gsub("^%s+", ""):gsub("%s+$", "")
      end

      local katex_args = {'--no-throw-on-error'}
      if elem.mathtype == 'DisplayMath' then
         table.insert(katex_args, '--display-mode')
      end

      return pandoc.RawInline(
         FORMAT, trim(pandoc.pipe("katex", katex_args, trim(elem.text))))
   end
end
