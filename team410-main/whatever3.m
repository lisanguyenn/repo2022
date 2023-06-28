for i = 1:2
    figure(1)
    title(append("EOF ", num2str(i), " by Location"))
    scatter(bigsmalldata(:, 3), bigsmalldata(:, 4), 25, bigsmalldata(:, i + 4), 'filled')
    colorbar
    plot(PCs1(i,:))
    xlabel('Week Number')
    title('Covid Principle Components by Week')
    F(i) = getframe(gcf) ;
    drawnow
end
  % create the video writer with 1 fps
  writerObj = VideoWriter('myVideo1.avi');
  writerObj.FrameRate = 0.5;
  % set the seconds per image
% open the video writer
open(writerObj);
% write the frames to the video
for i=1:length(F)
    % convert the image to a frame
    frame = F(i) ;    
    writeVideo(writerObj, frame);
end
% close the writer object
close(writerObj);