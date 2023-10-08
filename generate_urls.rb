require 'rubygems'
require 'jekyll'

Jekyll::Site.new(Jekyll.configuration({})).posts.docs.each do |post|
  puts post.url
end
