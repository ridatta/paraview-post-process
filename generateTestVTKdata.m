% This script creates test 3d volume data that can be imported into
% paraview. Use this code to create test data to verify the accuracy of
% post-processing code.
%%%%%%%%%%%%%%%%%%%%%%%%%
% Running this script will create a 3d cube of size 2R and resolution N
% and scalar values u assigned to tetrahedra in the mesh.
% The script will output tethrahedral data in .mat and .vtk formats
%%%%%%%%%%%%%%%%%%%%%%%
% Uses in-built delaunayTriangulation.m MATLAB function
% and writeVTKcell.m by Daniel Peterseim, 2009-11-07 to export as vtk

clc; close all; clear;

% create a cube
R = 50e-3; % size
N = 30; % resolution

% Cube points
x = linspace(-1,1,N) * R; 
y = x;
z = linspace(0,2,N) * R; 
[xx,yy,zz] = meshgrid(x,y,z); % cube
p = [xx(:), yy(:), zz(:)]; % points

% Trangulate
dt =  delaunayTriangulation(p);
tes = dt.ConnectivityList;
ic = incenter(dt);
u = 1 * ones(size(tes,1),1);  % scalar value

% sort by radial position
r = sqrt(ic(:,1).^2 + ic(:,2).^2); % radial magnitude
[r,id] = sort(r); % sort by radial length

% Specify how values change with radius
rval = 1 - 1/R * r; % lineary decreases from 1 at r = 0 to 0 at r = rmax
u(id) = rval; % assign radially varying values
u(id) = 1; % assign constant value

% Save MAT file
fname =  'u-1';
save([fname, '.mat'],'tes','p','u','ic'); 

% Save as PARAVIEW readable file
writeVTKcell(fname,tes,p,u);

% % Visualize - Uncomment to visualze data
% tetramesh(tes,p,u,'FaceAlpha',0.25); colormap hot; colorbar; hold on;
% plot3(ic(:,1),ic(:,2),ic(:,3),'*r'); 
% xlabel('x'); ylabel('y'); zlabel('z'); 
% 
% % Save as PARAVIEW readable file
% writeVTKcell(fname,tes,p,u);


