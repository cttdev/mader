#include <Eigen/Dense>
#include "spline_AStar.hpp"
#include "faster_types.hpp"
#include "utils.hpp"
#include "ros/ros.h"
#include "visualization_msgs/MarkerArray.h"
#include "visualization_msgs/Marker.h"
#include "decomp_ros_msgs/PolyhedronArray.h"
#include <decomp_ros_utils/data_ros_utils.h>  //For DecompROS::polyhedron_array_to_ros

int main(int argc, char **argv)
{
  ros::init(argc, argv, "testSplineAStar");
  ros::NodeHandle nh;
  ros::Publisher trajectories_found_pub =
      nh.advertise<visualization_msgs::MarkerArray>("A_star_trajectories_found", 1000, true);

  ros::Publisher jps_poly_pub = nh.advertise<decomp_ros_msgs::PolyhedronArray>("poly_jps", 1, true);

  int num_pol = 7;
  int deg_pol = 3;

  int samples_x = 7;  // odd number
  int samples_y = 7;  // odd number
  int samples_z = 7;  // odd number

  double fraction_voxel_size = 0.5;  // grid used to prune nodes that are on the same cell

  double runtime = 0.3;     //[seconds]
  double goal_size = 0.01;  //[meters]

  Eigen::Vector3d v_max(7.0, 7.0, 7.0);
  Eigen::Vector3d a_max(20.0, 20.0, 20.0);

  Eigen::Vector3d q0(-2.0, 0, 0);
  Eigen::Vector3d q1 = q0;
  Eigen::Vector3d q2 = q1;
  Eigen::Vector3d goal(2.0, 0, 0);

  double t_min = 0.0;
  double t_max = t_min + (goal - q0).norm() / (0.6 * v_max(0));

  ConvexHullsOfCurves hulls_curves;
  ConvexHullsOfCurve hulls_curve;

  ConvexHullsOfCurves_Std hulls_curves_std;
  ConvexHullsOfCurve_Std hulls_curve_std;
  Polyhedron_Std hull_std;

  std::vector<Point_3> points;

  points.push_back(Point_3(-1.0, -1.0, -3.0));
  points.push_back(Point_3(-1.0, -1.0, 3.0));
  points.push_back(Point_3(-1.0, 1.0, 3.0));
  points.push_back(Point_3(-1.0, 1.0, -3.0));

  points.push_back(Point_3(1.0, 1.0, 3.0));
  points.push_back(Point_3(1.0, 1.0, -3.0));
  points.push_back(Point_3(1.0, -1.0, 3.0));
  points.push_back(Point_3(1.0, -1.0, -3.0));

  CGAL_Polyhedron_3 hull_interval = convexHullOfPoints(points);

  for (int i = 0; i < num_pol; i++)
  {
    hulls_curve.push_back(hull_interval);  // static obstacle
  }
  hulls_curves.push_back(hulls_curve);  // only one obstacle

  ConvexHullsOfCurves_Std hulls_std = vectorGCALPol2vectorStdEigen(hulls_curves);
  vec_E<Polyhedron<3>> jps_poly = vectorGCALPol2vectorJPSPol(hulls_curves);

  // hull.push_back(Eigen::Vector3d(-1.0, -1.0, -700.0));
  // hull.push_back(Eigen::Vector3d(-1.0, -1.0, 700.0));
  // hull.push_back(Eigen::Vector3d(-1.0, 1.0, 700.0));
  // hull.push_back(Eigen::Vector3d(-1.0, 1.0, -700.0));

  // hull.push_back(Eigen::Vector3d(1.0, 1.0, 700.0));
  // hull.push_back(Eigen::Vector3d(1.0, 1.0, -700.0));
  // hull.push_back(Eigen::Vector3d(1.0, -1.0, 700.0));
  // hull.push_back(Eigen::Vector3d(1.0, -1.0, -700.0));

  // Assummes static obstacle
  /*  for (int i = 0; i < num_pol; i++)
    {
      hulls_curve.push_back(hull);
    }

    hulls_curves.push_back(hulls_curve);*/

  SplineAStar myAStarSolver(num_pol, deg_pol, hulls_std.size(), t_min, t_max, hulls_std);

  myAStarSolver.setq0q1q2(q0, q1, q2);
  myAStarSolver.setGoal(goal);

  myAStarSolver.setZminZmax(-1.0, 10.0);          // z limits for the search, in world frame
  myAStarSolver.setBBoxSearch(30.0, 30.0, 30.0);  // limits for the search, centered on q2
  myAStarSolver.setMaxValuesAndSamples(v_max, a_max, samples_x, samples_y, samples_z, fraction_voxel_size);

  myAStarSolver.setRunTime(runtime);
  myAStarSolver.setGoalSize(goal_size);

  myAStarSolver.setBias(2.0);
  myAStarSolver.setBasisUsedForCollision(myAStarSolver.MINVO);  // MINVO //B_SPLINE
  myAStarSolver.setVisual(false);

  std::vector<Eigen::Vector3d> q;
  std::vector<Eigen::Vector3d> n;
  std::vector<double> d;
  bool solved = myAStarSolver.run(q, n, d);

  std::vector<trajectory> all_trajs_found;
  myAStarSolver.getAllTrajsFound(all_trajs_found);

  visualization_msgs::MarkerArray marker_array_all_trajs;
  int increm = 1;
  int type = 6;
  double scale = 0.01;
  int j = 0;

  std::cout << "*********************************" << std::endl;

  std::cout << "size of all_trajs_found= " << all_trajs_found.size() << std::endl;

  for (auto traj : all_trajs_found)
  {
    visualization_msgs::MarkerArray marker_array_traj =
        trajectory2ColoredMarkerArray(traj, type, v_max.maxCoeff(), increm, "traj" + std::to_string(j), scale);
    // std::cout << "size of marker_array_traj= " << marker_array_traj.markers.size() << std::endl;
    for (auto marker : marker_array_traj.markers)
    {
      marker_array_all_trajs.markers.push_back(marker);
    }
    j++;
    type++;
  }

  std::cout << "size of marker_array_all_trajs.markers" << marker_array_all_trajs.markers.size() << std::endl;

  decomp_ros_msgs::PolyhedronArray poly_msg = DecompROS::polyhedron_array_to_ros(jps_poly);
  poly_msg.header.frame_id = "world";
  jps_poly_pub.publish(poly_msg);

  trajectories_found_pub.publish(marker_array_all_trajs);
  ros::spinOnce();

  /*
    vectorOfNodes2vectorOfStates()

        traj_committed_colored_ = stateVector2ColoredMarkerArray(data, type, par_.v_max, increm, name_drone_);
    pub_traj_committed_colored_.publish(traj_committed_colored_);*/

  if (solved == true)
  {
    std::cout << "This is the result" << std::endl;
    for (auto qi : q)
    {
      std::cout << qi.transpose() << std::endl;
    }
  }
  else
  {
    std::cout << "A* didn't find a solution" << std::endl;
  }

  std::cout << "Normal Vectors: " << std::endl;
  for (auto ni : n)
  {
    std::cout << ni.transpose() << std::endl;
  }

  std::cout << "D coefficients: " << std::endl;
  for (auto di : d)
  {
    std::cout << di << std::endl;
  }

  ros::spin();

  return 0;
}